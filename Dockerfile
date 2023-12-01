FROM registry.access.redhat.com/ubi8/ubi:latest

ENV CONFIG_PATH=/ccx-data-pipeline/config.yaml \
    VENV=/ccx-data-pipeline-venv \
    HOME=/ccx-data-pipeline \
    REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH" \
    PIP_CONSTRAINT=$HOME/constraints.txt

RUN dnf install --nodocs -y python3-pip unzip git-core python38 && \
    python3.8 -m venv $VENV && \
    curl -ksL https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem -o /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt && \
    curl -ksL https://certs.corp.redhat.com/certs/2022-IT-Root-CA.pem -o /etc/pki/ca-trust/source/anchors/2022-IT-Root-CA.pem && \
    update-ca-trust && \
    pip install --no-cache-dir -U pip setuptools && \
    pip install --no-cache-dir . && \
    pip install --no-cache-dir -r deployment-requirements.txt && \
    dnf remove -y git-core && \
    dnf clean all && \
    chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV

USER 1001

CMD ["sh", "-c", "ccx-data-pipeline $CONFIG_PATH"]
