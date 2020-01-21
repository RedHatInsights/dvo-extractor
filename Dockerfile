FROM registry.access.redhat.com/ubi8/ubi:latest

COPY . /ccx-data-pipeline

RUN yum -y install python3-pip git
RUN git clone https://github.com/RedHatInsights/insights-core.git && pip3 install -e insights-core
RUN git clone https://github.com/RedHatInsights/insights-core-messaging.git && pip3 install -e insights-core-messaging
RUN git -c http.sslVerify=false clone https://gitlab.cee.redhat.com/ccx/insights-ocp && pip3 install -e insights-ocp
RUN pip3 install -e /ccx-data-pipeline

ENTRYPOINT python3 -m insights_messaging /ccx-data-pipeline/config.yaml