#!/bin/bash
DART_FOLDER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKERFILE=${DART_FOLDER}"/worker/worker.json"
echo "{" >  ${WORKERFILE}
echo "\"python_home\" : \""$(which python)"\",">> ${WORKERFILE}
echo "\"module_prefix\" : \""$(pwd)"/example/\",">> ${WORKERFILE}
echo "\"output_directory\" : \""${HOME}"/feddart/tmp/\",">> ${WORKERFILE}
echo "}" >>  ${WORKERFILE}