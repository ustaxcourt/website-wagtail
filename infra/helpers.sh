#!/bin/bash

check_env_vars() {
  local missing_envs=()

  for env_var in "${required_env_vars[@]}"; do
    if [[ -z "${!env_var}" ]]; then
      missing_envs+=("$env_var")
    fi
  done

  if [[ ${#missing_envs[@]} -gt 0 ]]; then
    echo "Error: The following required environment variables are not set:"
    for missing_env in "${missing_envs[@]}"; do
      echo "  - $missing_env"
    done
    echo "Please set these variables and try again."
    exit 1
  fi
}
