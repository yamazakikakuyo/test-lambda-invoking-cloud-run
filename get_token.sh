# #!/usr/bin/env bash
# set -euo pipefail

# # 1) Export the Lambda execution role creds to env variables for WIF
# eval "$(aws configure export-credentials --format env)"

# # 2) Non-interactive login using your WIF credentials file
# GCLOUD_BIN="${GCLOUD_BIN:-/opt/google-cloud-sdk/bin/gcloud}"
# CRED_FILE="${AWS_WIF_CRED:-/opt/wif/aws-wif.json}"
# AUDIENCE="${GCP_AUDIENCE:-${SERVICE_URL:-}}"
# SA_EMAIL="${GCP_IMPERSONATE_SA:?Set GCP_IMPERSONATE_SA env to the target service account email}"

# # Ensure required inputs exist
# [ -f "$CRED_FILE" ] || { echo "WIF cred file not found at $CRED_FILE" >&2; exit 1; }
# [ -n "$AUDIENCE" ] || { echo "GCP_AUDIENCE or SERVICE_URL must be set" >&2; exit 1; }

# # Login with WIF JSON (non-interactive)
# "$GCLOUD_BIN" auth login --cred-file="$CRED_FILE" --quiet >/dev/null 2>&1

# # 3) Print the ID token (stdout must contain ONLY the token)
# "$GCLOUD_BIN" auth print-identity-token \
#   --audiences="$AUDIENCE" \
#   --impersonate-service-account="$SA_EMAIL"
