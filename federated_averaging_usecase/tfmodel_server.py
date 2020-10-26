import tensorflow as tf
from tensorflow import feature_column
from abc import ABC, abstractmethod

class AbstractModel(ABC):

    def __init__(self):
        self.model = None

    def get_model(self):
        if self.model is not None:
            return tf.keras.models.clone_model( self.model)
        else:
            raise ValueError("model is not available!!")

    def get_weights(self):
        if self.model is not None:
            return self.model.get_weights()
        else:
            raise ValueError("model weights are not available!!")

    def set_weights(self, new_model_weights):
        self.model.set_weights( new_model_weights)

def add_weekday_embedding(feature_columns): # adding three different holiday types on the weekday
    day = feature_column.categorical_column_with_vocabulary_list('weekday', [0,1,2,3,4,5,6,7,8,9])
    day_embedding = feature_column.embedding_column(day, dimension=2)
    
    feature_columns.append(day_embedding)

    return feature_columns

def add_holiday_embedding(feature_columns): # adding a new holiday column
    day = feature_column.categorical_column_with_vocabulary_list('weekday', [0,1,2,3,4,5,6])
    day_embedding = feature_column.embedding_column(day, dimension=2)
    
    holiday = feature_column.categorical_column_with_vocabulary_list('holiday', [0,1,2,3])
    holiday_embedding = feature_column.embedding_column(holiday, dimension=2)
    
    feature_columns.append(day_embedding)
    feature_columns.append(holiday_embedding)

    return feature_columns

def create_feature_colums():
    feature_columns = []
    hour = feature_column.categorical_column_with_vocabulary_list('hour', [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])
    hour_embedding = feature_column.embedding_column(hour, dimension = 4)
    month = feature_column.categorical_column_with_vocabulary_list('month', [1,2,3,4,5,6,7,8,9,10,11,12])
    month_embedding = feature_column.embedding_column(month, dimension = 2)
    feature_columns = []
    feature_columns.append(hour_embedding)
    feature_columns.append(month_embedding)
    return feature_columns

class MNIST(AbstractModel): 
    def __init__(self):
        super().__init__() 
        self.create_model()
        self.weights = None

    def create_model(self):
        model = tf.keras.models.Sequential([tf.keras.layers.Flatten(input_shape=(28, 28))
                                           , tf.keras.layers.Dense(128, activation='relu')
                                           , tf.keras.layers.Dropout(0.2)
                                           , tf.keras.layers.Dense(10)
                                           ]
                                          )
        self.model = model

class EmbeddingModelAirPollution(AbstractModel):

    def __init__( self
                , activation
                , activation_output
                , list_neurons_each_layer
                , type_feature_colums
                ):
        super().__init__() 
        self.create_model( activation
                         , activation_output
                         , list_neurons_each_layer
                         , type_feature_colums
                         )
        self.weights = None


    def create_model( self
                    , activation
                    , activation_output
                    , list_neurons_each_layer #[100, 200, 50]
                    , type_feature_colums
                    ):
        list_layers = []
        feature_columns = create_feature_colums()
        if type_feature_colums == "add_weekday":
            feature_columns = add_weekday_embedding(feature_columns)
        elif type_feature_colums == "add_holiday":
            feature_columns = add_holiday_embedding(feature_columns)
        feature_layer = tf.keras.layers.DenseFeatures(feature_columns)
        list_layers.append(feature_layer)
        list_layers.append(tf.keras.layers.Flatten())
        for neurons in list_neurons_each_layer:
            list_layers.append(tf.keras.layers.Dense( neurons, activation = activation))
        output = tf.keras.layers.Dense(1, activation = activation_output)
        list_layers.append(output)
        self.model = tf.keras.Sequential(list_layers)

    # train model on edge_device side !!
    def train_model( self   
                   , epochs
                   , batch_size
                   , learning_rate
                   , loss_function
                   , optimizer
                   , train_data
                   ):
        current_model = self.get_model()
        optimizer = tf.keras.optimizers.RMSprop(learning_rate)
        current_model.compile(optimizer= optimizer, loss = loss_function , metrics = ['mae','mse'])
        current_model = self.get_weights()  
        current_model.fit(train_data, epochs = epochs)
        current_model_weights = current_model.get_weights()
        self.update_weights(current_model_weights)

    def eval_model( self, data):
        y_pred = model.predict(data)
        r = r2_score(classe[train_partition:test_partition],y_pred)
        mae = mean_absolute_error(classe[train_partition:test_partition],y_pred)

