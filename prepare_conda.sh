#!/bin/bash
conda deactivate
conda env remove -n fed_dart

echo -n "Do you want to install tensorflow [(y)es,(n)o]? "
read tf

if [ "$tf" == "y" ]; then
    echo "installing with tensorflow..."
    conda create -n fed_dart python=3.7.3 tensorflow=2.1 pip numpy requests dill 
else
    echo "installing without tensorflow..."
    conda create -n fed_dart python=3.9 pip numpy requests dill
fi
