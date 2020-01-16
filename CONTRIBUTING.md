# Contributing



## General code rules
For docstrings we're following [Google documentation conventions](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google).

All methods meant to be used by end-user *must be* documented - **no exceptions!**


## Submitting a pull request

*Note: Every PR requires at least one review from at least one of the core review members. List of members are available on [Settings/Members page](https://gitlab.cee.redhat.com/ccx/insights-ocp/-/project_members)*

Before you submit your pull request consider the following guidelines:

* Fork the repository and clone your fork
  * open the following URL in your browser: https://github.com/RedHatInsights/ccx-data-pipeline/
  * click on the 'Fork' button (near the top right corner)
  * open your forked repository in browser: https://github/YOURNAME/ccx-data-pipeline/
  * click on the 'Clone' button to get a command that can be used to clone the repository

* Make your changes in a new git branch:

     ```shell
     git checkout -b bug/my-fix-branch master
     ```

* Create your patch, **ideally including appropriate test cases**
* Include documentation that either describe a change to a behavior or the changed capability to an end user
* Commit your changes using **a descriptive commit message**. If you are fixing an issue please include something like 'this closes issue #xyz'

* Push your branch to GitHub:

    ```shell
    git push origin bug/my-fix-branch
    ```

* When opening a pull request, select the `master` branch as a base.
* Mark your pull request with **[WIP]** (Work In Progress) to get feedback but prevent merging (e.g. [WIP] Update CONTRIBUTING.md)
* If we suggest changes then:
  * Make the required updates
  * Push changes to git (this will update your Pull Request):
    * You can add new commit
    * Or rebase your branch and force push to your GitLab repository:

    ```shell
    git rebase -i master
    git push -f origin bug/my-fix-branch
    ```
That's it! Thank you for your contribution!
