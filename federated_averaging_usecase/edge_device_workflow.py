from tfmodel_edge_device import *

class EdgeDeviceWorklow():
    
    def init_model(model_structure, device_name):
        model_edge_device = ModelEdge()
        model_edge_device.init_model(model_structure)
        model_edge_device.save(device_name)

    def train_model( global_weights
                   , dict_training_hyperparameter
                   , device_name
                   ):
        model_edge_device = ModelEdge()
        model_edge_device.load_model(device_name)
        model_edge_device.update_weights(global_weights)
        model_edge_device.train_model(dict_training_hyperparameter)
        model_edge_device.save(device_name)
        return model_edge_device.get_weights()
    
    def eval_model( self
                  , global_weights
                  ):
        pass
