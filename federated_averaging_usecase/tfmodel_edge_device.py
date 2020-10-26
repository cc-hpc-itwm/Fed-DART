import tensorflow as tf
from tensorflow import feature_column

def save_model(model, device_name,  filepath):
    save_path = filepath + "/" + device_name 
    model.save(save_path)

def load_model(device_name, filepath):
    load_path = filepath + "/" + device_name 
    model = tf.keras.models.load_model(load_path)
    return model

FILEPATH = "/home/scratch/fed_dart_temporary"

class ModelEdge():

    def __init__(self):
        self.model = None

    def init_model(self, model_structure):
        self.model = tf.keras.models.model_from_json(model_structure)

    def save(self, device_name):
        save_model(self.model, device_name, FILEPATH)
    
    def load_model(self, device_name):
        self.model = load_model(device_name, FILEPATH)

    def get_model(self):
        if self.model is not None:
            return self.model
        else:
            raise ValueError("model is not available!!")

    def get_weights(self):
        if self.model is not None:
            return self.model.get_weights()
        else:
            raise ValueError("model weights are not available!!")

    def update_weights(self, new_weights):
        if self.model is not None:
            return self.model.set_weights(new_weights)
        else:
            raise ValueError("model is not available!!")

    def update_model(self, new_model):
        self.model = new_model

    def train_model( self   
                   , dict_training_hyperparameter
                   ):
        mnist = tf.keras.datasets.mnist
        (x_train, y_train), (x_test, y_test) = mnist.load_data(path = FILEPATH + '/mnist.npz')
        x_train, x_test = x_train / 255.0, x_test / 255.0
        current_model = self.get_model()
        optimizer = tf.keras.optimizers.Adam(learning_rate = dict_training_hyperparameter["learning_rate"] )
        loss_function = tf.keras.losses.SparseCategoricalCrossentropy()
        current_model.compile(optimizer = optimizer, loss = loss_function , metrics = ['mae','mse'])  
        current_model.fit( x_train
                         , y_train
                         , epochs = dict_training_hyperparameter["epochs"]
                         , batch_size = dict_training_hyperparameter["batch_size"]
                         , verbose = 0
                         )
        self.update_model(current_model)
        #current_model_weights = current_model.get_weights()
        #self.update_weights(current_model_weights)

    def eval_model( self, data):
        y_pred = model.predict(data)
        r = r2_score(classe[train_partition:test_partition],y_pred)
        mae = mean_absolute_error(classe[train_partition:test_partition],y_pred)
