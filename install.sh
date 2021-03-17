#!/bin/bash
./prepare_conda.sh

echo "entering dart directory..."
cd dart

echo -n "Is your system based on x86 [(y)es,(n)o]? (Installation will default to x86) "
read -t 5 setting


if [ "$setting" == "y" ]; then
    echo "Installing for x86 machines..."
    #echo "Downloading files..."
    tar xvf dart_x86_64.tar.gz
elif [ "$setting" == "n" ]; then
    echo "Installing for ARM machines..."
    #echo "Downloading files..."
    tar xvf dart_arm.tar.gz
else
    echo 
    echo " Timeout: Default installation for x86 machines..."
    tar xvf dart_x86_64.tar.gz
fi

echo "leaving dart directory..."
cd ..

echo "generating worker config..."
./dart/dart/generate_worker_config.sh