import json
import os
import subprocess
import requests

SERVICE_URL = os.environ.get("SERVICE_URL", "https://test-secure-api-601511081631.us-central1.run.app/")

def _get_token():
    # Run the bash script and capture only the token from stdout
    token = subprocess.check_output(
        ["bash", "/opt/scripts/get_token.sh"],
        text=True
    ).strip()
    if not token:
        raise RuntimeError("No token returned by /opt/scripts/get_token.sh")
    return token

def lambda_handler(event, context):
    token = _get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(SERVICE_URL, headers=headers, timeout=30)

    # Return exactly what Cloud Run replied (status + body)
    return {
        "statusCode": resp.status_code,
        "body": resp.text
    }
