# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

[![GitLab Pages](https://img.shields.io/badge/%20-GitLab%20Pages-informational)](https://ccx.pages.redhat.com/ccx-data-pipeline/)

## Description

CCX Data Pipeline service intends to get Insights gathered archives and analyzes
them using the Insights framework in order to generate a report with the rules
hit by the content of the archive.

This report is published back in order to be consumed by other services.

## Smoke Tests

To run smoke tests automatically when you make a merge request you need to add
@devtools-bot as a mainteiner of the cloned repository.

1. Go to the cloned repository you create to contribute to this project,
the link looks like so: `https://gitlab.cee.redhat.com/<your-gitlab-username>/ccx-data-pipeline/`
2. on the top left corner click on: "Project information" and then "Members"
3. add @devtools-bot and select the "Mainteiner" role

You can skip steps 1 and 2 if you go to the link `https://gitlab.cee.redhat.com/<your-gitlab-username>/ccx-data-pipeline/-/project_members` directly.

This will allow the smoke test to run automatically every merge request you make.

## Benchmark tests

In `test/benchmark_test.py` file there are benchmark tests to measure the service
performance. To perform those test the pipeline must be running, either 
[locally](https://ccx.pages.redhat.com/ccx-docs/howto/local_edp.html) or
in an [ephemeral cluster](https://ccx.pages.redhat.com/ccx-docs/howto/ephemeral_env.html).
If you're running tests locally you can tweak the tests configuration by setting the
proper environment variables (a list with description can be found in `deploy/benchmark.yaml`).
To run the test in an ephemeral cluster you need to add the following service to 
your `test.yaml` file:

```
- name: ext-pipeline-benchmark
      host: gitlab
      repo: ccx/ccx-data-pipeline
      path: deploy/benchmark.yaml
      ref: master
      parameters:
        IMAGE: quay.io/cloudservices/ccx-data-pipeline
        IMAGE_TAG: latest
```

The last step is to launch the test and read the output:

`python test/benchmark_test.py`

## Documentation

Documentation is hosted on Gitlab Pages
<https://ccx.pages.redhat.com/ccx-data-pipeline/>.
Sources are located in [docs](https://gitlab.cee.redhat.com/ccx/ccx-data-pipeline/-/tree/master/docs).
