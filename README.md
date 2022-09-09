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

## Documentation

Documentation is hosted on Gitlab Pages
<https://ccx.pages.redhat.com/ccx-data-pipeline/>.
Sources are located in [docs](https://gitlab.cee.redhat.com/ccx/ccx-data-pipeline/-/tree/master/docs).
