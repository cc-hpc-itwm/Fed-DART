
import pytest

from feddart.deviceSingle import DeviceSingle
from feddart.dartRuntime import DartRuntime



#------------------------fixtures-----------------------------------------------------------    
@pytest.fixture
def deviceSingle():
    server = "https://127.0.0.0.1:7777"
    client_key = "000"
    error_probability = 0
    dartRuntime = DartRuntime(server, client_key, error_probability, True)
    name = "device_one"
    ipAdress = "client1"
    port = 2883
    deviceSingle = DeviceSingle( name = name, ipAdress = ipAdress, port = port, dartRuntime = dartRuntime
                               , physicalName = None, hardwareConfig = None, taskDict = {}, initTask = None)
    return deviceSingle

@pytest.fixture
def taskName_one():
    taskName = "task_one"
    return taskName

@pytest.fixture
def finishedtaskName_one():
    taskName = "finished_task_one"
    return taskName

@pytest.fixture
def taskParameter_one():
    taskParameter = {"param1": "hello", "param2": "world"}
    return taskParameter

@pytest.fixture
def finished_task_result_one():
    taskResult = { 'duration': 5, 'result': {'result_0': 10, 'result_1': None}}
    return taskResult

@pytest.fixture(autouse=True)
def device_first_task(deviceSingle, taskName_one, taskParameter_one):
    deviceSingle.addTask(taskName_one, taskParameter_one)
    return deviceSingle

@pytest.fixture(autouse=True)
def device_addFinishedTask_task(deviceSingle, finished_task_result_one): 
    deviceSingle._addFinishedTask("finished_task_one", finished_task_result_one)
    return deviceSingle
    
 #---------------------------------------------------------------------------------------   
## test adding tasks
def test_addTask_wrong_Dict_entries(deviceSingle, taskName_one, taskParameter_one):
    assert deviceSingle.openTaskDict == {taskName_one: taskParameter_one}
                     
def test_addTask_task_already_added(deviceSingle, taskName_one, taskParameter_one):
    # add the same task again
    with pytest.raises(KeyError, match="already in openTaskDict!"):
        deviceSingle.addTask(taskName_one, taskParameter_one)

def test_addTask_check_dict(deviceSingle, taskName_one, taskParameter_one):
    taskName_two = "task_two"
    taskParameter_two = {"param1": "hello", "param2": "world"}
    deviceSingle.addTask(taskName_two, taskParameter_two)
    assert deviceSingle.openTaskDict == { taskName_one: taskParameter_one, taskName_two: taskParameter_two}

## test finished tasks
def test_AddFinishedTask(deviceSingle, finishedtaskName_one, finished_task_result_one):
    assert deviceSingle.finishedTaskDict == {finishedtaskName_one: finished_task_result_one}
        
def test_addFinishedTask_task_already_added(deviceSingle, finishedtaskName_one, finished_task_result_one):
    with pytest.raises(KeyError, match="already in finishedTaskDict!"):
        deviceSingle._addFinishedTask(finishedtaskName_one, finished_task_result_one)

def test_addFinishedTask_extend_dict(deviceSingle, finishedtaskName_one, finished_task_result_one):
    tasktwo = "task_two"
    deviceSingle._addFinishedTask(tasktwo, finished_task_result_one)
    assert deviceSingle.finishedTaskDict == {finishedtaskName_one: finished_task_result_one, tasktwo : finished_task_result_one}



def test_isOpenTask(deviceSingle, taskName_one, taskParameter_one):
    "Check if taskName is in openTaskDict"
    assert deviceSingle.isOpenTask(taskName_one)
    # there should be no task two
    assert not deviceSingle.isOpenTask("task_two")

def test_RemoveOpenTask(deviceSingle, taskName_one, taskParameter_one):
    "Try to remove tasks from openTaskDict"
    taskName_two = "task_two"
    deviceSingle.addTask(taskName_two, taskParameter_one)
    # remove task_one
    deviceSingle.removeOpenTask(taskName_one)
    assert not deviceSingle.isOpenTask(taskName_one)
    # fails when there is more than task_two
    assert deviceSingle.openTaskDict == {taskName_two: taskParameter_one}

def test_GetOpenTaskParameter(deviceSingle, taskName_one, taskParameter_one):
    "Get the parameter of an open task"
    assert deviceSingle.getOpenTaskParameter(taskName_one) == taskParameter_one
    with pytest.raises(KeyError, match="Open task with name"):
        deviceSingle.getOpenTaskParameter("task_two")

def test_GetFinishedTaskResult(deviceSingle, finishedtaskName_one, finished_task_result_one):
    "Get the result of a finished task"
    assert deviceSingle._getFinishedTaskResult(finishedtaskName_one) == finished_task_result_one
    
    with pytest.raises(KeyError, match="Finished task with name"):
        deviceSingle._getFinishedTaskResult("task_two")

def test_hasTask(deviceSingle, taskName_one, finished_task_result_one):
    "Check if the device has a task with such an name in open or finished tasks"
    assert deviceSingle.hasTask("task_one")
    assert deviceSingle.hasTask("finished_task_one")
    assert not deviceSingle.hasTask("task_three")


   