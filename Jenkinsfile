@Library("github.com/RedHatInsights/insights-pipeline-lib@v3") _

node {
  pipelineUtils.cancelPriorBuilds()

  pipelineUtils.runIfMasterOrPullReq {
    runStages()
  }
}

def runStages() {
  openShiftUtils.withNode(
    image: "docker-registry.upshift.redhat.com/ccx-dev/ccx-builder:latest",
    jenkinsSlaveImage: "docker-registry.engineering.redhat.com/centralci/jnlp-slave-base:1.5",
    cloud: "jenkins-csb-ccx",
    namespace: "jenkins-csb-ccx"
  ) {
    checkout scm

    gitUtils.stageWithContext("Install-dependencies") {
      sh "pip install -U pip setuptools wheel"
      withCredentials([string(credentialsId: "insights-droid-github-token", variable: "TOKEN")]) {
        sh "pip install git+https://${TOKEN}@github.com/RedHatInsights/ccx-ocp-core"
        sh "pip install git+https://${TOKEN}@github.com/RedHatInsights/ccx-rules-ocp"
      }
      def install = sh(script:"pip install -e .[dev]", returnStatus: true)
    }
    if (install != 0) {
      error("install failed")
    }

    gitUtils.stageWithContext("Pycodestyle") {
      def pycodeStyle = sh(script: "pycodestyle", returnStatus: true)
    }
    if (pycodeStyle != 0) {
      error("pycodestyle failed")
    }


    gitUtils.stageWithContext("Run-unit-tests") {
      def tests = sh(script: "pytest -vv test", returnStatus: true)
    }
    if (tests != 0) {
      error("tests failed")
    }
    junit "junit.xml"
  }
}
