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
    cloud: "jenkins-csb-ccx",
    namespace: "jenkins-csb-ccx"
  ) {
    checkout scm

    gitUtils.stageWithContext("Install-dependencies") {
      withCredentials([string(credentialsId: "insights-droid-github-token", variable: "TOKEN")]) {
        sh "pip install git+https://${TOKEN}@github.com/RedHatInsights/ccx-ocp-core"
        sh "pip install git+https://${TOKEN}@github.com/RedHatInsights/ccx-rules-ocp"
      }
      sh "pip install -e .[dev]"
    }

    gitUtils.stageWithContext("Pycodestyle") {
      sh "pycodestyle"
    }

    gitUtils.stageWithContext("Pydocstyle") {
      sh "pydocstyle controller test"
    }

    gitUtils.stageWithContext("Run-unit-tests") {
      sh "pytest --junitxml=junit.xml --cov --cov-config=.coveragerc test"
    }
    
    junit "junit.xml"
  }
}
