#!/bin/bash
# remove old conda environment
ENVNAME=fed_dart_env

eval "$(conda shell.bash hook)"

# switch to base environment
conda deactivate
# remove old conda env
conda env remove -n ${ENVNAME}

echo -n "Do you want to install tensorflow [(y)es,(n)o]? (Default: without tensorflow) "
read -t 5 tf

# create new environment and install w/wo tensorflow
if [ "$tf" == "y" ]; then
    echo "installing with tensorflow..."
    conda create -y -n ${ENVNAME} python=3.7.3 tensorflow=2.1 pip numpy requests dill 
elif [ "$tf" == "n" ]; then
    echo "installing without tensorflow..."
    conda create -y -n ${ENVNAME} python=3.9 pip numpy requests dill
else
    echo 
    echo " Timeout: installing without tensorflow"
    conda create -y -n ${ENVNAME} python=3.9 pip numpy requests dill 
fi

echo "Install fed-dart package..."
conda activate ${ENVNAME}
pip install .
echo "done!"