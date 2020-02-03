FROM registry.access.redhat.com/ubi8/ubi:latest

ARG GITHUB_API_TOKEN

ENV CONFIG_PATH=/ccx-data-pipeline/config.yaml \
    VENV="/ccx-data-pipeline-venv" \
    HOME=/ccx-data-pipeline \
    GIT_ASKPASS=/git-askpass.sh

WORKDIR $HOME

COPY . .

RUN dnf -y --setopt=tsflags=nodocs install python3-pip git unzip && \
    python3 -m venv $VENV

ENV PATH="$VENV/bin:$PATH"

RUN pip install -U --no-cache-dir pip wheel setuptools && \
    echo "echo $GITHUB_API_TOKEN" > $GIT_ASKPASS && \
    chmod +x /git-askpass.sh && \
    pip install --no-cache-dir -e . && \
    dnf remove -y git && \
    dnf clean all && \
    rm $GIT_ASKPASS && \
    chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV

USER 1001

CMD ["sh", "-c", "python3 -m insights_messaging $CONFIG_PATH"]
