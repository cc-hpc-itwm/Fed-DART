import numpy as np

def FederatedAveraging(list_models_weights):
    #TODO: implement function, that all models have the same structure
    number_of_layers = len(list_models_weights[0])
    number_of_models = len(list_models_weights)
    averaged_list_weights = []
    for layer_index in range(number_of_layers):
        shape_layer_weights = np.shape(list_models_weights[0][layer_index])
        cummulated_weights = np.zeros(shape_layer_weights)
        for model_weights in list_models_weights:
            cummulated_weights += model_weights[layer_index]
        cummulated_weights /= number_of_models
        averaged_list_weights.append(cummulated_weights)
    return averaged_list_weights
    """
    number_of_layers = len(list_models[0].layers)
    number_of_models = len(list_models)
    for layer_index in range(number_of_layers):
        shape_layer_weights = np.shape(list_models[0].layers[layer_index].get_weights()[0])
        shape_layer_bias = np.shape(list_models[0].layers[layer_index].get_weights()[1])
        cummulated_weights = np.zeros(shape_layer_weights)
        cummulated_bias = np.zeros(shape_layer_bias)
        for model in list_models:
            cummulated_weights += model.layers[layer_index].get_weights()[0]
            cummulated_bias += model.layers[layer_index].get_weights()[1]
        cummulated_weights /= number_of_models
        cummulated_bias /= number_of_models
        global_model.layers[layer_index].set_weights([cummulated_weights, cummulated_bias])
    return global_model
    """