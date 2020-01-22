FROM registry.access.redhat.com/ubi8/ubi:latest

ENV CONFIG_PATH=/ccx-data-pipeline/config.yaml \
    VENV="/ccx-data-pipeline-venv" \
    HOME=/ccx-data-pipeline

WORKDIR $HOME

COPY . .

RUN dnf -y --setopt=tsflags=nodocs install python3-pip git && \
    python3 -m venv $VENV

ENV PATH="$VENV/bin:$PATH"

RUN pip install -U --no-cache-dir pip wheel setuptools && \
    curl -ksL https://password.corp.redhat.com/RH-IT-Root-CA.crt \
         -o /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt && \
    update-ca-trust && \
    pip install --no-cache-dir -e . && \
    dnf remove -y git && \
    dnf clean all && \
    chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV

USER 1001

CMD ["sh", "-c", "python3 -m insights_messaging $CONFIG_PATH"]
