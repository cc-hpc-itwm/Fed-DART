#!/bin/bash
./prepare_conda.sh

echo "entering dart directory..."
cd dart

echo -n "Is your system based on x86 [(y)es,(n)o]? "
read setting


if [ "$setting" == "y" ]; then
    echo "Installing for x86 machines..."
    #echo "Downloading files..."
    tar xvf dart_x86_64.tar.gz
else
    echo "Installing for ARM machines..."
    #echo "Downloading files..."
    dart xvf dart_arm.tar.gz
fi

echo "leaving dart directory..."
cd ..

echo "generating worker config..."
./dart/dart/generate_worker_config.sh