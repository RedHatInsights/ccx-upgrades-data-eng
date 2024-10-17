#!/bin/bash
# Copyright 2022 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -exv


# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="ccx-data-pipeline"  # name of app-sre "application" folder this component lives in
REF_ENV="insights-production"
COMPONENT_NAME="ccx-upgrades-data-eng"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/ccx-upgrades-data-eng"
COMPONENTS="ccx-upgrades-data-eng ccx-upgrades-inference dvo-writer ccx-redis ccx-smart-proxy ccx-mock-ams ccx-upgrades-rhobs-mock ccx-upgrades-sso-mock" # space-separated list of components to laod
COMPONENTS_W_RESOURCES="ccx-upgrades-data-eng"  # component to keep
CACHE_FROM_LATEST_IMAGE="true"
DEPLOY_FRONTENDS="false"
# Set the correct images for pull requests.
# pr_check in pull requests still uses the old cloudservices images
EXTRA_DEPLOY_ARGS="--set-parameter ccx-upgrades-data-eng/IMAGE=quay.io/cloudservices/ccx-upgrades-data-eng"

export IQE_PLUGINS="ccx"
# Run all pipeline and ui tests
export IQE_MARKER_EXPRESSION="(upgrades and not ui)"
export IQE_FILTER_EXPRESSION=""
export IQE_REQUIREMENTS_PRIORITY=""
export IQE_TEST_IMPORTANCE=""
export IQE_CJI_TIMEOUT="30m"
export IQE_SELENIUM="false"
export IQE_ENV="ephemeral"
export IQE_ENV_VARS="DYNACONF_USER_PROVIDER__rbac_enabled=false"


function build_image() {
   source $CICD_ROOT/build.sh
}

function deploy_ephemeral() {
   source $CICD_ROOT/deploy_ephemeral_env.sh
}

function run_smoke_tests() {
   # component name needs to be re-export to match ClowdApp name (as bonfire requires for this)
   export COMPONENT_NAME="ccx-smart-proxy"
   source $CICD_ROOT/cji_smoke_test.sh
   source $CICD_ROOT/post_test_results.sh  # publish results in Ibutsu
}


# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
echo "creating PR image"
build_image

echo "deploying to ephemeral"
deploy_ephemeral

echo "PR smoke tests disabled"
run_smoke_tests
