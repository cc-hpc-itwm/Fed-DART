# Fed-DART: beta version 0.1
Fed-DART is a Python-based Federated Learning Framework for x86 and ARM architectures. It supports different kinds of fedeated learning workflows to be flexible enough for your use-case.
Fed-DART can be used together with any machine-learning library written in Python. The flexibility of Fed-DART is demonstrated for scikit-learn and tensorflow examples.

## General Overview
Fed-DART has three main components:

* Local machine of the End-User (Data Scientist)
* DART-Server
* DART-Clients (e.g Raspberry Pi)
<img src="/images/worklow_feddart.png" width="50%" height="50%" />

## End-User

The End-User must install the pip-package feddart on his local machine.
Feddart itself communicates via REST-API with the DART server in the background.
Feddart has an easy and comfortable user-interface to shedule tasks for the federated learning clients.
The aspects like communication, connection handling, logging are handled internally in feddart. The end
user is only responsible for the federated learning algorithm.

### DART-Server
The DART-Server is responsible for communcation and task sheduling to the clients.The communication between
serer and clients is done via DART, a Python wrapper around GPI-Space.

### DART-Clients
The client has the computational power for executing a local federated learning task with sharing the local parameters afterwards.
The client must have a Linux system, the hardware architecture can be x86 or ARM. 

Fed-DART also supports  a test-modus without needing a server and clients. The test mode runs on the local machine of the end-users
with the conceps of folders as virtual clients.\
<img src="/images/workflow_feddart_testmode.png" width="50%" height="50%" />

## Setting-up DART-Server and DART-Clients on Linux system.
The following steps are only necessary if you want to set up the DART-Server and DART-Clients, not in the case of test modus.
Clone this repo and cd into the dart folder and choose the right version(depends on your target platform). Unzip the tar file. If you want to
start the server go into the folder /bin and execute dart-server.exe. The server will connect over SSH to the clients, therefore the server needs the public key of the clients (important: for connecting over SSH server and clients must have the same user name atm, a fix is WIP)
In the case you want to configure the DART-Client go into the folder /worker and open the file worker.json. Set the path like that
```python
{
  "python_home": path to python home or your conda environement (e.g "/home/user/miniconda3/envs/beta_version/") ,
  "module_prefix": path to the folder of the files (e.g "/home/user/feddart/client1/"),
  "output_directory": path for logging std output (e.g. "/var/tmp/")
}
```
## Getting Started: Examples 
We have three simple examples to sketch the general workflow of using Fed-DART. For the sake of brevity we look on the 
federated averaging example on the MNIST dataset.
The code which runs on end users local machine can be found in examples/federated_averaging.
Before executing the learning algorithm the end-user must initialize the WorkflowManager, which 
is the user-interface to Fed-DART.
```python
from feddart.workflowManager import WorkflowManager
manager = WorkflowManager()
```
For some use-case it's necessary, that an initialization task is executed before an learning task on every client.
In the current example, the client must know the model structure before training the model itself (we only send 
the weights during learning to the clients). Therefore the use can create an init task at the begining. Fed-DART
automatically send this init task to clients, also to later connected ones, and checks if the init task was sucessfully
executed on the client, before accepting new tasks. The server and server-known clients can 
be started through the function startFedDART.
```python
manager.createInitTask( parameterDict = {"model_structure": global_model.to_json()}
                      , filePath = "client_learning"
                      , executeFunction = "init"
                      )
manager.startFedDART( runtimeFile = "../serverFile.json" 
                    , deviceFile = "../deviceFile.json"
                    , maximal_numberDevices = 100
                    )
```
Fed-DART will support multiple federated learning workflows. In the current stage of development, we only support the case of 
sending tasks (taskType 1) to specific devices.The case of sending tasks to random devices, which fullfill certain requirements, will be included soon.
```python
manager.startTask( taskType = 1 
                 , taskName = task_name
                 , parameterDict =  { "device_one": { "global_model_weights": global_model_weights
                                                    , "batch_size": 64
                                                    , "epochs": 2
                                                    }
                                    , "device_two": { "global_model_weights": global_model_weights
                                                    , "batch_size": 8
                                                    , "epochs": 4
                                                    }
                                    }
                , filePath = "client_learning" 
                , executeFunction = "learn"
                )
while manager.getTaskStatus(task_name) != manager.TASK_STATUS_FINISHED:
    time.sleep(3)
taskResult = manager.getTaskResult(task_name) #return all results which are currently available

```
To excute this function we will look now on client side into the file client_learning and the two functions
init und learn. To use this function together with feddart you must decorate them with @feddart.
The init function has no return. If an exception is thrown during the init task it will be automatically returned.

```python
from feddart.messageTranslator import feddart

@feddart
def init(model_structure):
    client_model = keras.models.model_from_json(model_structure)
    #then store it somewhere 

@feddart
def learn(global_model_weights, batch_size, epochs):
    cwd = os.path.dirname(os.path.abspath(__file__))
    client_model = keras.models.load_model(cwd + "/" + MODEL_NAME)
    client_model.compile( optimizer = "sgd", loss = "mse")
    client_model.set_weights(global_model_weights)
    x_train, y_train = get_mnist_train_data()
    client_model.fit( x_train
                    , y_train
                    , epochs = epochs
                    , batch_size = batch_size
                    )
    return client_model.get_weights()
```

## Using Fed-DART as pip package
To use feddart as pip package on your local machine cd into the repo and type
into the console
```python
pip install .
```
Afterwards you can integrate feddart in any project with from feddart.workflowManager import WorkflowManager.

## Functions in WorkflowManager
* Instantiation of WorkflowManager
```python
manager = WorkflowManager( testMode #True or False
                         , errorProbability #probability for throwing errors in test mode, set it atm to 0
                         )
```
* Creation of init task. Must be done before connect to DART-server
```python
manager.createInitTask( parameterDict #dictionary with parameter names and values
                      , filePath #python file of executeFunction
                      , executeFunction #function which should be executed
                      )
```
* Connect to DART-Server
```python
manager.startFedDART( runtimeFile #settings how to connect to server
                    , deviceFile #devices, to which the server should connect
                    , maximal_numberDevices #maximal amount of devices for server
                    )
```

* Create a task. Fed-Dart will check the task requirements and accepts the task if
  the requirements are fullfilled.
```python
manager.startTask( taskType #atm only type one is supported
                 , taskName #unique name of task (e.g "task_one)
                 , parameterDict #dict of format { "device_one": {"para1": 5}
                                #                , "device_two: {"para1": 10}}
                 , filePath #python file of executeFunction
                 , executeFunction #function which should be executed
                 )
```
* Get the status of a task by name. Result can be in "in queue", "in progress" or "finished"
```python
manager.getTaskStatus( taskName) #return: "in queue", "in progresss" or "finished
```
* At any time we can get the results of the task. The return will be a list of
  task results from the already finished clients. To get more informations about the API
  of the task results, we refer to the documentation "API of task results" below.
```python
manager.getTaskResult( taskName) #return: list of task results
```

* Tasks can be removed from the DART-server (e.g. the task is finished). Already fetched 
  results from the server will be available locally (function will be implemented soon).
```python
manager.stopTask( taskName) 
```

* remove Device from the DART-Server.
```python
manager.removeDevice(deviceName) 
```

* Get the name of all devices, which are connected to the DART-server.
```python
manager.getAllDeviceNames() 
```

* Shut down the DART-server
```python
manager.stopFedDART() 
```
## API of task results
To access a task result we support multiple options as sketched in the hello world example.
* get duration of task and from which device
```python
taskResult.deviceName
taskResult.duration
```
* get the task results as list or dictionary
```python
taskResult.resultDict #format like {"result_0": 5, "result_1": 2 }
taskResult.resultList #format like [5,2]
```
## Getting Started
We start with the example in the hello_world folder. We assume for experimental testing that the clients are running on your local machine. In a real-world scenario the file hello_world_client.py will be run on edge devices, the file hello_world_server.py on your local machine. FedDART runs in background on your local machine and will communicate with the clients over the DART server. \
The IP adress of the server is stored in runtimeFile.json, such that FedDART knows to which server it should connect. Moreover we assume for this first example that we know the clients (e.g edge devices) to which we want to connect. The device names together with the ipAdress are stored in deviceFile.json.
Following steps are necessary to exceute this example (we assume the same folder structur and code as in the page Set up FedDART for experimental usage
1. cd beta_version/dart/dart/worker and set in worker.json module prefix to /home/user_name/beta_version/examples/hello_world/
2. cd beta_version/dart/dart/bin and ./dart-server.exe \
  2.1 in case you want to start the dart server on styx/carme, please use:\
    2.1.1 carme_prepare_dart_from_pip \
    2.1.2 ./dart-server.exe --gspc-ssh-private-key "${CARME_SSHDIR}/id_rsa_${CARME_JOB_ID}" --gspc-ssh-public-key "${CARME_SSHDIR}/id_rsa_${CARME_JOB_ID}.pub" --gspc-ssh-port "${SSHD_PORT}"

3. Open a new terminal
4. in case ssh is not running and you have sudo permissions: sudo service ssh start
5. cd beta_version/examples/hello_world and execute file hello_world_server.py

## Set up FedDART for experimental usage

For experimental usage we deliver Fed-Dart together with DART.\
**Requirements**\
Linux on x86 architecture. If you are using Windows you can use WSL 1 instead.\
**Installation**\
Steps for installation
1. Clone this git repo in  a folder e.g. feddart
2. cd feddart/
3. git checkout -b your_branch origin/beta_version
4. create conda environment with python and pip installed, e.g name env_feddart \
  4.1 conda create -n env_feddart \
  4.2 install pip, e.g. conda install pip 
5. pip install .
6. cd dart/ and tar -xf dart_x86_64.tar
7. cd dart/worker/
8. open worker.json file:\
  8.1 remove entry "name" \
 8.2 Set path to your conda environement in python_home e.g. /home/user_name/miniconda3/envs/env_feddart/ \
 8.3 Remove empty space between "module_prefix" and : .Set path to folder where the executable files are 
     in "module_prefix" e.g /home/user_name/beta_version/examples\
 8.4 Set path were the logging should be saved

## Further remarks
Fed-DART is currently under development and therefore room for improvement.
If you have any issues, suggestions for new features or new example use-cases 
which can be intregated in our repo feel free to contact
nico.weber@itwm.fraunhofer.de.
We also have a Teams channel for announcing news regarding Fed-DART. If you want to 
join this channel, contact us.
