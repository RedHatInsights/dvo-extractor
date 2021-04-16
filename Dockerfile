FROM registry.access.redhat.com/ubi8/ubi:latest

ARG GITHUB_API_TOKEN

ENV CONFIG_PATH=/ccx-data-pipeline/config.yaml \
    VENV="/ccx-data-pipeline-venv" \
    HOME=/ccx-data-pipeline \
    GIT_ASKPASS=/git-askpass.sh

WORKDIR $HOME

RUN dnf -y --setopt=tsflags=nodocs install python3-pip git unzip && \
    python3 -m venv $VENV && echo "echo $GITHUB_API_TOKEN" > $GIT_ASKPASS && \
    chmod +x /git-askpass.sh

COPY . $HOME

ENV PATH="$VENV/bin:$PATH"

RUN pip install -U --no-cache-dir pip setuptools && \
    pip install -r requirements.txt && \
    pip install --no-cache-dir -e . && \
    dnf remove -y git && \
    dnf clean all && \
    rm $GIT_ASKPASS && \
    chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV

RUN curl -L -o /usr/bin/haberdasher \
    https://github.com/RedHatInsights/haberdasher/releases/download/v0.1.3/haberdasher_linux_amd64 && \
    chmod 755 /usr/bin/haberdasher

USER 1001

ENTRYPOINT ["/usr/bin/haberdasher"]
CMD ["sh", "-c", "ccx-data-pipeline $CONFIG_PATH"]
