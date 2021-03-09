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
executed on the client, before acceptig new tasks. The server and server-known clients can 
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

```python
from feddart.messageTranslator import feddart

@feddart
def init(model_structure):
    try: 
        client_model = keras.models.model_from_json(model_structure)
        #then store it somewhere, see code 
        return True
    except:
        return False

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

## Further remarks
Fed-DART is currently under development and therefore room for improvement.
If you have any issues, suggestions for new features or new example use-cases 
which can be intregated in our repo feel free to contact
nico.weber@itwm.fraunhofer.de.
We also have a Teams channel for announcing news regarding Fed-DART. If you want to 
join this channel, contact us.
