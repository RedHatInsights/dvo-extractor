@Library("github.com/RedHatInsights/insights-pipeline-lib@v3") _

node {
  pipelineUtils.cancelPriorBuilds()

  pipelineUtils.runIfMasterOrPullReq {
    runStages()
  }
}

def runStages() {
  openShiftUtils.withNode(
    image: "docker-registry.upshift.redhat.com/ccx-dev/ccx-e2e-base:latest",
    jenkinsSlaveImage: pipelineVars.centralCIjenkinsSlaveImage,
    cloud: "openshift",
    namespace: "ccx-explore"
  ) {
    checkout scm

    gitUtils.stageWithContext("Install-dependencies") {
      sh "pip install -U pip setuptools wheel"
      withCredentials([string(credentialsId: "insights-droid-github-token", variable: "TOKEN")]) {
        sh "echo 'echo ${TOKEN}' > /tmp/git_askpass.sh"
        sh "chmod +x /tmp/git_askpass.sh"
      }
      withEnv(["GIT_ASKPASS=/tmp/git_askpass.sh"]) {
        sh "pip install -r requirements.txt"
        sh "pip install -e .[dev]"
      }
    }

    gitUtils.stageWithContext("Black formatter") {
      sh "black --line-length 100"
    }

    gitUtils.stageWithContext("Pycodestyle") {
      sh "pycodestyle"
    }

    gitUtils.stageWithContext("Pydocstyle") {
      sh "pydocstyle ccx_data_pipeline test"
    }

    gitUtils.stageWithContext("Run-unit-tests") {
      sh "pytest --junitxml=junit.xml --cov --cov-config=.coveragerc test"
    }

    gitUtils.stageWithContext("Pylint") {
      sh "pylint ccx_data_pipeline test"
    }


    junit "junit.xml"
  }
}
