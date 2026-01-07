[ -z "${AWS_ACCOUNT_ID}" ] && echo "You must have AWS_ACCOUNT_ID set in your environment" && exit 1
[ -z "${GITHUB_SHA}" ] && echo "You must have GITHUB_SHA set in your environment" && exit 1

aws iam attach-role-policy --role-name github-workflow-deployer --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/deployer-policy
gh workflow run production_deploy.yml --ref production -f commit_sha=${GITHUB_SHA}
