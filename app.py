import json
import os
import subprocess
import requests
import sys

SERVICE_URL        = os.environ.get("SERVICE_URL", "https://test-secure-api-601511081631.us-central1.run.app/")
GCP_AUDIENCE       = os.environ.get("GCP_AUDIENCE", SERVICE_URL)
GCP_IMPERSONATE_SA = os.environ.get("GCP_IMPERSONATE_SA", "aws-cloud-run-invoker@ai-deployment-475315.iam.gserviceaccount.com")
AWS_WIF_CRED       = os.environ.get("AWS_WIF_CRED", "/opt/wif/aws-wif.json")
GCLOUD_BIN         = os.environ.get("GCLOUD_BIN", "/opt/google-cloud-sdk/bin/gcloud")

def _get_token():
    # Run the bash script and capture only the token from stdout
    if not AWS_WIF_CRED or not os.path.isfile(AWS_WIF_CRED):
        print(f"WIF cred file not found at {AWS_WIF_CRED}", file=sys.stderr)
        sys.exit(1)

    if not GCP_AUDIENCE:
        print("GCP_AUDIENCE or SERVICE_URL must be set", file=sys.stderr)
        sys.exit(1)
    try:
        print("Generate AWS Key")
        aws_key = subprocess.check_output(["bash", "-c", "aws configure export-credentials --format process"], text=True).strip()
        aws_key = json.loads(aws_key)

        for x, y in [("AWS_ACCESS_KEY_ID", "AccessKeyId"),
                    ("AWS_SECRET_ACCESS_KEY", "SecretAccessKey"),
                    ("AWS_SESSION_TOKEN", "SessionToken")]:
            os.environ[x] = aws_key[y]
        
        print("Login with Cred File")
        subprocess.run([
            GCLOUD_BIN,
            "auth",
            "login",
            f"--cred-file={AWS_WIF_CRED}",
            "--quiet"],
            check=True)

        print("Generate Token")
        token = subprocess.run(
            [
                GCLOUD_BIN, "auth", "print-identity-token",
                f"--audiences={GCP_AUDIENCE}",
                f"--impersonate-service-account={GCP_IMPERSONATE_SA}"
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )

        print("DataType Token:", type(token))
        print("Value Token:", token)
        if not token:
            raise RuntimeError("No token returned by /opt/scripts/get_token.sh")
        return token
    except subprocess.CalledProcessError as e:
        print("Command Subprocess failed!")
        print("Return code:", e.returncode)
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
    

def lambda_handler(event, context):
    token = _get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Headers:", headers)

    resp = requests.post(SERVICE_URL, headers=headers, timeout=30)

    # Return exactly what Cloud Run replied (status + body)
    return {
        "statusCode": resp.status_code,
        "body": resp.text
    }
