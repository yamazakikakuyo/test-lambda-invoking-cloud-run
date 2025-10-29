# Base: AWS Lambda Python runtime
FROM public.ecr.aws/lambda/python:3.11

# Install tools: curl, unzip, tar (for installers)
# Then install AWS CLI v2 and Google Cloud SDK (tarball install)
RUN yum -y install tar gzip unzip curl && yum clean all && \
    curl -sSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip" && \
    unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws /tmp/awscliv2.zip && \
    curl -sSL "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-471.0.0-linux-x86_64.tar.gz" -o /tmp/gcloud.tar.gz && \
    mkdir -p /opt && tar -C /opt -xzf /tmp/gcloud.tar.gz && \
    /opt/google-cloud-sdk/install.sh --quiet && \
    ln -s /opt/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud && \
    rm -f /tmp/gcloud.tar.gz

# Add Python deps into Lambda task root
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt -t "${LAMBDA_TASK_ROOT}"

# Code & scripts
COPY handler.py ${LAMBDA_TASK_ROOT}/app.py
COPY scripts/get_token.sh /opt/scripts/get_token.sh
RUN chmod +x /opt/scripts/get_token.sh

# Your WIF credentials file (you will provide this at build time)
# If you name it differently, also set AWS_WIF_CRED env accordingly.
COPY aws-wif.json /opt/wif/aws-wif.json

# Useful env vars (override in Lambda console or at 'docker run' time)
ENV SERVICE_URL="https://test-secure-api-601511081631.us-central1.run.app/"
ENV GCP_AUDIENCE="${SERVICE_URL}"
ENV GCP_IMPERSONATE_SA="aws-cloud-run-invoker@ai-deployment-475315.iam.gserviceaccount.com"
ENV AWS_WIF_CRED="/opt/wif/aws-wif.json"
ENV GCLOUD_BIN="/opt/google-cloud-sdk/bin/gcloud"

# Lambda entrypoint (module.function)
CMD ["app.lambda_handler"]
