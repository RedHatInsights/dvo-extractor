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
    jenkinsSlaveImage: "docker-registry.engineering.redhat.com/centralci/jnlp-slave-base:1.5",
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

    gitUtils.stageWithContext("Run-unit-tests") {
      sh "pytest --junitxml=junit.xml -vv test"
    }

    junit "junit.xml"
  }
}
