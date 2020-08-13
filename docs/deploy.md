---
layout: page
nav_order: 8
---
# Deploy

`ccx-data-pipeline` runs in [cloud.redhat.com](https://cloud.redhat.com) and
it's a part of the same testing and promoting routines. There are three
environments: CI, QA and PROD. The code should pass tests in QA env before it
goes to PROD. cloud.redhat.com team uses jenkins, OCP and
[ocdeployer](https://github.com/bsquizz/ocdeployer) for code deploying. All
deployment configs are stored in
[e2e-deploy](https://github.com/RedHatInsights/e2e-deploy) git repository.

