# 2021-03-19
## Added
   - Exceptions from clients are returned to end user
## Changed
   - Internally changes of formatting and abstract classes
## API Changes
   - WorkflowManager.startTask returns True or False now
   - init function on client dont't need a return value anymore

# 2021-06-02
## Added
   - Test environment with Docker Containers
   - Support that clients can connect on their own to the server
   - User can fetch the currently connected devices from server
## Changed
   - The examples are updated, such that the all currently connected devices are used

# 2021-09-21
## Added
   - Development environment with Docker Containers
   - Logging 
   - User can fetch new connected devices from server
   - New class collection, to handle devices over multiple learning rounds (e.g
     Personalized Federated Learning)
