from feddart.messageTranslator import feddart
import tensorflow as tf
import os 
from tensorflow import keras
from tensorflow.keras.utils import to_categorical
MODEL_NAME = "client_model"

def get_mnist_train_data():
    raw_data = tf.keras.datasets.mnist.load_data()
    x_train = raw_data[0][0] / 255 - 0.5
    y_train = to_categorical(raw_data[0][1])
    x_train = x_train.reshape((-1, 28 * 28))

    return x_train, y_train

@feddart
def init(model_structure): 
    client_model = keras.models.model_from_json(model_structure)
    client_model.compile(loss = "mse")
    cwd = os.path.dirname(os.path.abspath(__file__))
    directory = cwd + os.sep + MODEL_NAME
    if not os.path.exists(directory):
        os.makedirs(directory)
    client_model.save(directory)

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


