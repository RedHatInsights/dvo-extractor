/*
 * Requires: https://github.com/RedHatInsights/insights-pipeline-lib
 */

@Library("github.com/RedHatInsights/insights-pipeline-lib@v3") _

scmVars = checkout scm

 if (currentBuild.currentResult == "SUCCESS" && env.CHANGE_TARGET == "stable" && env.CHANGE_ID) {
    execSmokeTest (
        ocDeployerBuilderPath: "ccx-data-pipeline/ccx-data-pipeline",
        ocDeployerComponentPath: "ccx-data-pipeline/ccx-data-pipeline",
        ocDeployerServiceSets: "ccx-data-pipeline,platform,platform-mq",
        iqePlugins: ["iqe-ccx-plugin"],
        pytestMarker: "ccx_smoke",
    )
}
