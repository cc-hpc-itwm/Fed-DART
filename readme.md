# Fed-DART: beta version 0.1
Fed-DART is a Python-based Federated Learning Framework for x86 and ARM architectures. It supports different kinds of fedeated learning workflows to be flexible enough for your use-case.
Fed-DART can be used together with any machine-learning library written in Python. The flexibility of Fed-DART is demonstrated for scikit-learn and tensorflow examples.

## General Overview
Fed-DART has three main components:

* Local machine of the End-User (Data Scientist)
* DART-Server
* DART-Clients (e.g Raspberry Pi)
<img src="/images/general_workflow_feddart.png" width="50%" height="50%" />

## End-User

The End-User must install the pip-package feddart on his local machine.
Feddart itself communicates via REST-API with the DART server in the background.
Feddart has an easy and comfortable user-interface to schedule tasks for the federated learning clients.
Other aspects such as communication, connection handling, logging are handled by feddart. The end
user is only responsible for the federated learning algorithm.

### Logging
Logging is by default set to warning level. In case you want to get more log-information, please set the flag
``` -log (0,1,2,3,4,5) ``` to adjust the log level accordingly. More information is provided by ```--help```
### DART-Server
The DART-Server is responsible for communication and task sheduling on the client devices. The communication between
server and clients is done via DART, a Python wrapper around GPI-Space.

### DART-Clients
The client has the computational power for executing a local federated learning task with sharing the local parameters afterwards.
The client must have a Linux system, the hardware architecture can be x86 or ARM. 

Fed-DART also supports  a test-mode without needing a server and clients. The test mode runs on the local machine of the end-users
with the concept of folders as virtual clients.\
<img src="/images/test_workflow_feddart.png" width="50%" height="50%" />
 
## Test Environment with DART-Server and DART-Client as Docker-Container.
For experimental usage we recommend to use Docker. We provide a docker-compose file for automatically setting up the infrastructure. <br>
<img src="/images/docker_workflow_feddart.png" width="50%" height="50%" />
<br>
This will create a container for the DART-Server and two DART-Client containers.  
Following steps are needed: <br>
- cd docker/ 
- docker-compose build 
- docker-compose up -d (starts the infrastructure)
- docker-compose down (shut down the infrastructure after experiments)

**NOTE:** The used Docker-container are not optimized for security and size.

## Getting Started: Examples 
We have three simple examples to sketch the general workflow of Fed-DART usage.
All examples have two options
```python
python example_program -m test/real -ep 0
```
The option -m switch between test or real mode. The option -ep is needed for test mode to have an error probability. 
For the sake of brevity we look at the federated averaging example using MNIST dataset.
The code which runs on end user's local machine can be found in examples/federated_averaging.
Before executing the learning algorithm, end-user must initialize the WorkflowManager which 
is the user-interface to Fed-DART.
```python
from feddart.workflowManager import WorkflowManager
manager = WorkflowManager()
```
For some use-case, it's necessary that an initialization task is executed on every client device before any learning task.
In the current example, client must know the model structure before training the model itself (we only send 
the model's weights during learning process to the clients). Therefore the user can create an init task at the begining.
Fed-DART automatically sends this init task to clients, also to the ones connected later on, and checks if the init task was sucessfully executed on all clients before accepting new tasks. The server and server-known clients can 
be started through the function startFedDART.
```python
manager.createInitTask( parameterDict = {"model_structure": global_model.to_json()}
                      , filePath = "client_learning"
                      , executeFunction = "init"
                      )
manager.startFedDART( runtimeFile = "../serverFile.json" 
                    , maximal_numberDevices = 100
                    )
```
Fed-DART will support multiple federated learning workflows. In the current stage of development, we only support the case of sending tasks (taskType 1) to specific devices. The case of sending tasks to devices, which fulfills certain hardware requirements, will be included soon. <br>
To specify the parameterDict for the task, fetch the currently connected devices from the DART-server and set parameters.
```python
list_devices = manager.getAllDeviceNames()
parameterDict = {}
for idx, device in enumerate(list_devices):
	parameterDict[device] = { "global_model_weights": global_model_weights 
							, "batch_size": 10*idx + 8
							, "epochs": idx + 1 
							}
```
Afterwards start the task.
```python
handle = manager.startTask( taskType = 1 
                          , parameterDict = parameterDict
                          , filePath = "client_learning" 
                          , executeFunction = "learn"
                          )
while manager.getTaskStatus(handle) != manager.TASK_STATUS_FINISHED:
    time.sleep(3)
taskResult = manager.getTaskResult(handle) #return all results which are currently available

```
To execute this function we will now look on client side in the file client1/client_learning and the two functions
init and learn. To use these functions together with feddart you must decorate them with @feddart.
The init function has no return value. If an exception is thrown during the init task it will be automatically returned.

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
in the console
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
* Creation of init task. Must be done before connecting to DART-server
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

* Create a task. Fed-Dart will check the task requirements and accept the task if
  the requirements are fullfilled. A unique identifier is returned to the user. If this identifier 
  is equal to None the task wasn't accepted.
```python
handle = manager.startTask( taskType #atm only type one is supported
                          , parameterDict #dict of format { "device_one": {"para1": 5}
                                         #                , "device_two: {"para1": 10}}
                          , filePath #python file of executeFunction
                          , executeFunction #function which should be executed
                          )
```
* Get the status of a task by name. Result can be in "in queue", "in progress" or "finished"
```python
manager.getTaskStatus( handle) #return: "in queue", "in progresss" or "finished
```
* At any time we can get the results of the task. The return will be a list of
  task results from the already finished clients. To get more information about the API
  of the task results, we refer to the documentation "API of task results" below.
```python
manager.getTaskResult( handle) #return: list of task results
```

* Tasks can be removed from the DART-server (e.g. the task is finished). Already fetched 
  results from the server will be available locally (function will be implemented soon).
```python
manager.stopTask( handle) 
```

* remove Device from the DART-Server.
```python
manager.removeDevice(deviceName) 
```

* Get the name of all devices, which are connected to the DART-server.
```python
manager.getAllDeviceNames() 
```

* Get the name of all devices, which are new since the last call
  of manager.getAllDeviceNames.
```python
manager.getNewDeviceNames()
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

## API of collection
For some use-cases like Personalized Federated Learning it makes sense to group 
certain devices to a collection for a better handling over different global learning rounds.
To create a collection call the workflowmanger with the property 
```python
manager.createCollection(["device_0", "device_1"])
```
together with a list of the device names.
Devices can be added or removed to a collection
```python
collection.addDevicebyName("device_3")
collection.removeDevicebyName("device_0")
```
A list with all active devices in a collection can 
be fetched with
```python
collection.ActiveDeviceNames
```

## Further remarks
Fed-DART is currently under development and therefore room for improvement.
If you have any issues, suggestions for new features or new example use-cases 
which can be integrated in our repo feel free to contact
jens.krueger@itwm.fraunhofer.de.
We also have a Teams channel for announcing news regarding Fed-DART. If you want to 
join this channel, contact us.
