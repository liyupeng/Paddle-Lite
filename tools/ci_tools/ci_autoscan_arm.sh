#!/bin/bash
# Start the CI task of unittest for op and pass.
set -x
set -e

#####################################################################################################
# 1. global variables, you can change them according to your requirements
#####################################################################################################
# Python version
PYTHON_VERSION=3.9
# Absolute path of Paddle-Lite source code.
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
WORKSPACE=${SHELL_FOLDER%tools/ci_tools*}
# Common options
TARGET_LIST="ARM,OpenCL,Metal"


####################################################################################################
# Functions of operate unit test
# Arguments:
#   target_name: can be ARM or OpenCL or Metal
# Globals:
#   WORKSPACE
####################################################################################################
function auto_scan_test {
  local target_name=$1

  cd $WORKSPACE/lite/tests/unittest_py/rpc_service
  sh start_rpc_server.sh

  cd $WORKSPACE/lite/tests/unittest_py/op/
  unittests=$(ls)
  for test in ${unittests[@]}; do
    if [[ "$test" =~ py$ ]];then
      python3.8 $test --target=$target_name
    fi
  done

  cd $WORKSPACE/lite/tests/unittest_py/pass/
  unittests=$(ls)
  for test in ${unittests[@]}; do
    if [[ "$test" =~ py$ ]];then
      python3.8 $test --target=$target_name
    fi
  done
}

####################################################################################################
# Functions of compiling test.
# Arguments:
#   --target_list: can be ARM,OpenCL or ARM,Metal
# Globals:
#   WORKSPACE, PYTHON_VERSION
####################################################################################################
function compile_publish_inference_lib {
  local target_list=""
  # Extract arguments from command line
  for i in "$@"; do
    case $i in
      --target_list=*)
        target_list="${i#*=}"
        shift
        ;;
      *)
        shift
        ;;
    esac
  done

  local targets=(${target_list//,/ })
  local build_opencl=OFF
  local build_metal=OFF
  for target in ${targets[@]}; do
    if [[ "$target" == "OpenCL" ]]; then
      build_opencl=ON
    elif [[ "$target" == "Metal" ]]; then
      build_metal=ON
    fi
  done

  if [[ "$build_opencl" == "ON" && "$build_metal" == "ON" ]]; then
    echo "ERROR: OpenCL and Metal both turn on, which will cause unittests for Metal crash. You can only turn on one option."
    exit 1
  fi

  cd $WORKSPACE

  # Remove Compiling Cache
  rm -rf build.macos.*

  # Step1. Compiling python installer on mac M1
  local cmd_line="./lite/tools/build_macos.sh --with_python=ON --with_opencl=$build_opencl --with_metal=$build_metal --with_arm82_fp16=ON --python_version=$PYTHON_VERSION arm64"
  $cmd_line

  # Step2. Checking results: cplus and python inference lib
  local whl_path=$(find ./build.macos.armmacos.armv8.* -name *whl)
  if [[ -z "$whl_path" ]]; then
    # Error message.
    echo "**************************************************************************************"
    echo -e "$whl_path not found!"
    echo -e "Compiling task failed on the following instruction:\n $cmd_line"
    echo "**************************************************************************************"
    exit 1
  fi

  # Step3. Install whl and its depends
  python$PYTHON_VERSION -m pip install --force-reinstall $whl_path
  python3.8 -m pip install -r ./lite/tests/unittest_py/requirements.txt
}

function run_test() {
  local target_list=$1
  local targets=(${target_list//,/ })

  for target in ${targets[@]}; do
    auto_scan_test $target
  done
}

function pipeline() {
  # Compile
  compile_publish_inference_lib --target_list=$1

  # Run unittests
  run_test $1

  # Uninstall paddlelite
  python$PYTHON_VERSION -m pip uninstall -y paddlelite
  echo "Success for targets:" $1
}

function main() {
  # Parse command line.
  for i in "$@"; do
    case $i in
      --target_list=*)
        TARGET_LIST="${i#*=}"
        shift
        ;;
      *)
        echo "Unknown option, exit"
        exit 1
        ;;
    esac
  done

  local targets=(${TARGET_LIST//,/ })
  for target in ${targets[@]}; do
    if [[ "$target" == "OpenCL" ]]; then
      pipeline "ARM,OpenCL"
    elif [[ "$target" == "Metal" ]]; then
      pipeline "Metal"
    fi
  done

  echo "Success for targets:" $TARGET_LIST
}

main $@
