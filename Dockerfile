FROM registry.access.redhat.com/ubi9-minimal:latest

ENV CONFIG_PATH=/dvo-extractor/config.yaml \
    VENV=/dvo-extractor-venv \
    HOME=/dvo-extractor \
    REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

ADD https://certs.corp.redhat.com/certs/2022-IT-Root-CA.pem https://certs.corp.redhat.com/certs/Current-IT-Root-CAs.pem /etc/pki/ca-trust/source/anchors/

WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH"

RUN microdnf install --nodocs -y python3.11 unzip tar git-core && \
    python3.11 -m venv $VENV && \
    update-ca-trust && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install . && \
    microdnf remove -y git-core && \
    microdnf clean all && \
    rpm -e --nodeps sqlite-libs krb5-libs libxml2 readline pam openssh openssh-clients && \
    chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV


USER 1001

CMD ["sh", "-c", "dvo-extractor $CONFIG_PATH"]
