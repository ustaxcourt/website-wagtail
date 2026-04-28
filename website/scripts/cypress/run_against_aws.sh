#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_against_aws.sh --mode <run|open> [options]

Options:
  --mode <run|open>            Cypress mode (required)
  --aws-env <dev-web|train-web|sandbox>
                               Named lower environment
  --sandbox-name <name>        Sandbox prefix for URL construction
                               (<name>-sandbox-web.ustaxcourt.gov)
  --base-url <https://...>     Explicit Cypress base URL override
  --secret-id <name>           AWS Secrets Manager secret id (default: website_secrets)
  --region <aws-region>        AWS region (default: AWS_DEFAULT_REGION or us-east-1)
  --browser <browser>          Browser passed to Cypress (default: chrome)
  --include-admin              Include admin validation specs
  --skip-health-check          Skip preflight HTTP health check
  --spec <spec-glob>           Optional Cypress --spec filter

Examples:
  ./scripts/cypress/run_against_aws.sh --mode run --aws-env dev-web
  ./scripts/cypress/run_against_aws.sh --mode run --aws-env train-web --include-admin
  ./scripts/cypress/run_against_aws.sh --mode run --base-url https://alice-sandbox-web.ustaxcourt.gov
  ./scripts/cypress/run_against_aws.sh --mode open --aws-env sandbox --sandbox-name alice
EOF
}

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: '$cmd' is required but not installed." >&2
    exit 1
  fi
}

mode=""
aws_env=""
sandbox_name=""
base_url=""
secret_id="website_secrets"
region="${AWS_DEFAULT_REGION:-us-east-1}"
browser="chrome"
include_admin=false
skip_health_check=false
spec=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      mode="$2"
      shift 2
      ;;
    --aws-env)
      aws_env="$2"
      shift 2
      ;;
    --sandbox-name)
      sandbox_name="$2"
      shift 2
      ;;
    --base-url)
      base_url="$2"
      shift 2
      ;;
    --secret-id)
      secret_id="$2"
      shift 2
      ;;
    --region)
      region="$2"
      shift 2
      ;;
    --browser)
      browser="$2"
      shift 2
      ;;
    --include-admin)
      include_admin=true
      shift
      ;;
    --skip-health-check)
      skip_health_check=true
      shift
      ;;
    --spec)
      spec="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: Unknown argument '$1'" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$mode" != "run" && "$mode" != "open" ]]; then
  echo "Error: --mode must be 'run' or 'open'." >&2
  usage
  exit 1
fi

if [[ -z "$base_url" ]]; then
  case "$aws_env" in
    dev-web|train-web)
      base_url="https://${aws_env}.ustaxcourt.gov"
      ;;
    sandbox)
      if [[ -z "$sandbox_name" ]]; then
        echo "Error: --sandbox-name is required when --aws-env sandbox is used." >&2
        exit 1
      fi
      base_url="https://${sandbox_name}-sandbox-web.ustaxcourt.gov"
      ;;
    "")
      echo "Error: provide either --base-url or --aws-env." >&2
      exit 1
      ;;
    *)
      echo "Error: unsupported --aws-env '$aws_env'. Use dev-web, train-web, sandbox, or pass --base-url." >&2
      exit 1
      ;;
  esac
fi

require_command aws
require_command jq
require_command npx
require_command curl

echo "Loading admin credentials from AWS Secrets Manager secret '$secret_id' in '$region'..."
secret_json=$(aws secretsmanager get-secret-value \
  --secret-id "$secret_id" \
  --region "$region" \
  --query SecretString \
  --output text 2>/dev/null || true)

if [[ -z "$secret_json" || "$secret_json" == "None" ]]; then
  repo_root=$(cd "$(dirname "$0")/../../.." && pwd)
  load_secrets_script="$repo_root/infra/load-secrets.sh"
  if [[ -f "$load_secrets_script" ]]; then
    echo "Direct secret lookup failed. Trying fallback via infra/load-secrets.sh..."
    set +u
    source "$load_secrets_script"
    set -u
    if [[ -n "${CYPRESS_ADMIN_PASSWORD:-}" || -n "${ADMIN_PASSWORD:-}" || -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
      admin_username="${CYPRESS_ADMIN_USERNAME:-${ADMIN_USERNAME:-admin}}"
      admin_password="${CYPRESS_ADMIN_PASSWORD:-${ADMIN_PASSWORD:-${DJANGO_SUPERUSER_PASSWORD:-}}}"
    fi
  fi
fi

if [[ -z "${admin_password:-}" ]]; then
  if [[ -z "$secret_json" || "$secret_json" == "None" ]]; then
    echo "Error: secret '$secret_id' has no SecretString payload, and infra/load-secrets.sh fallback did not provide admin credentials." >&2
    exit 1
  fi
fi

if [[ -z "${admin_password:-}" ]]; then
  admin_username=$(echo "$secret_json" | jq -r '.CYPRESS_ADMIN_USERNAME // .ADMIN_USERNAME // "admin"')
  admin_password=$(echo "$secret_json" | jq -r '.CYPRESS_ADMIN_PASSWORD // .ADMIN_PASSWORD // .DJANGO_SUPERUSER_PASSWORD // empty')
fi

if [[ -z "$admin_password" || "$admin_password" == "null" ]]; then
  echo "Error: could not find admin password in '$secret_id'. Expected one of: CYPRESS_ADMIN_PASSWORD, ADMIN_PASSWORD, DJANGO_SUPERUSER_PASSWORD" >&2
  exit 1
fi

run_stamp=$(date +%Y%m%d-%H%M%S)
label="$aws_env"
if [[ -z "$label" ]]; then
  label="custom"
fi
artifacts_dir="cypress/artifacts/${label}/${run_stamp}"
mkdir -p "$artifacts_dir"

echo "Running Cypress against: $base_url"
echo "Artifacts will be copied to: $artifacts_dir"

if [[ "$skip_health_check" != "true" ]]; then
  http_status=$(curl -sSL -o /dev/null -w "%{http_code}" "$base_url" || echo "000")
  if [[ "$http_status" -ge 500 || "$http_status" == "000" ]]; then
    echo "Error: Preflight health check failed for '$base_url' (HTTP $http_status)." >&2
    echo "The target AWS environment appears unavailable. Skipping Cypress execution." >&2
    cat > "$artifacts_dir/metadata.txt" <<EOF
mode=${mode}
base_url=${base_url}
aws_env=${aws_env}
sandbox_name=${sandbox_name}
secret_id=${secret_id}
region=${region}
include_admin=${include_admin}
browser=${browser}
run_timestamp=${run_stamp}
health_check_status=${http_status}
health_check_failed=true
exit_code=65
EOF
    exit 65
  fi
fi

cypress_cmd=(
  npx cypress "$mode"
  --browser "$browser"
  --config "baseUrl=${base_url}"
  --env "ADMIN_USERNAME=${admin_username},ADMIN_PASSWORD=${admin_password}"
)

if [[ -n "$spec" ]]; then
  cypress_cmd+=(--spec "$spec")
fi

set +e
CYPRESS_INCLUDE_ADMIN_VALIDATION="$include_admin" \
  "${cypress_cmd[@]}"
cypress_exit=$?
set -e

for folder in screenshots videos downloads; do
  if [[ -d "cypress/${folder}" ]]; then
    mkdir -p "$artifacts_dir/${folder}"
    cp -R "cypress/${folder}/." "$artifacts_dir/${folder}/"
  fi
done

cat > "$artifacts_dir/metadata.txt" <<EOF
mode=${mode}
base_url=${base_url}
aws_env=${aws_env}
sandbox_name=${sandbox_name}
secret_id=${secret_id}
region=${region}
include_admin=${include_admin}
skip_health_check=${skip_health_check}
browser=${browser}
run_timestamp=${run_stamp}
exit_code=${cypress_exit}
EOF

if [[ $cypress_exit -ne 0 ]]; then
  echo "Cypress exited with status ${cypress_exit}." >&2
  echo "Review artifacts in: $artifacts_dir" >&2
  exit $cypress_exit
fi

echo "Cypress completed successfully. Artifacts: $artifacts_dir"
