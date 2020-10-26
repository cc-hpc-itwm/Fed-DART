import numpy as np
import pandas as pd
import tensorflow as tf
import torch
import copy
import torch.nn as nn
import time
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
import torch.optim as optim
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from torch.utils.data import TensorDataset, DataLoader
from syft.frameworks.torch.fl import utils
import syft as sy
import math
import datetime
import matplotlib.pyplot as plt
from tensorflow import feature_column
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


#DataLoader and Prerprocessing in own module
#Step 1: Create and Manipulate Data Frame
holidays = pd.read_csv('C:/Users/Enislay_PC/.spyder-py3/Air_polution/data/holidays_new.csv', sep=';', parse_dates=[0])
traffic_left = pd.read_csv('C:/Users/Enislay_PC/.spyder-py3/Air_polution/data/traffic_left.csv',  parse_dates=[1]).dropna(how='any', axis=0).reset_index(drop = True)
traffic_left.pop('index')

stats_left = traffic_left.describe().transpose()
traffic_left['q']=(traffic_left['q']-stats_left['mean']['q'])/stats_left['std']['q']
traffic_left['b']=(traffic_left['b']-stats_left['mean']['b'])/stats_left['std']['b']
traffic_left['hour'] = [x.hour for x in traffic_left.ts]
traffic_left['weekday'] = [x.weekday() for x in traffic_left.ts]
traffic_left['month'] = [x.month for x in traffic_left.ts]
traffic_left['year'] = [x.year for x in traffic_left.ts]



def add_holidays1(data, holidays):
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'public holiday'].Date),"weekday"] = 7
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'bridge day'].Date),"weekday"] = 8
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'partial holiday'].Date),"weekday"] = 9
    data.pop('ts')    
    
    
def add_holidays2(data, holidays):#adding a new features with 4 categories, 3 is "normal" and 0,1 and 2 are the 3 holidays categories
    data["holiday"] = 3
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'public holiday'].Date),"holiday"] = 0
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'bridge day'].Date),"holiday"] = 1
    data.loc[data.ts.dt.normalize().isin(holidays[holidays.Type == 'partial holiday'].Date),"holiday"] = 2
    data.pop('ts')


def add_holidays(data, holidays): # switch between option 1 and 2
    add_holidays1(data, holidays)


#where is this function needed ?
def to_closest_month_start(dataset, index):
    res = index
    while (res <= max(dataset.index)) and ((res not in dataset.index) or dataset.loc[res].hour != 0.0):
        res = res + 1
    print(str(index) + ' => ' + str(res))
    return res

#preparing training for the learning stage
#only calendar features in the training set, target is the traffic volume
# ts,q,b
# data format 2014-05-01 00:00:00+00:00,31.25,0.5875
add_holidays(traffic_left, holidays)
target = traffic_left.pop('q') #feature to be predicted
traffic_left.pop('b')


# ditributing data per nodes
test_sample = 12 # last M months we want to forecast.
#option 1: Let N be the number of nodes, we distribute the data evenly across all nodes,respecting the sequence. 
#option 2: Let M be the number of months we want in each node. Then the number of nodes is calculated N = Total_months / M




"""Create an function that splits the data before loading !!
def create_data_from_indexes(inputs, target, start, end, batch_size):
    train = tf.data.Dataset.from_tensor_slices((dict(inputs[start:end]), target[start:end]))
    print("------ Dataset_" + str(inputs['year'].iloc[start]) +" from: \n " +str(inputs.iloc[start]) + " \n Until: \n "+ str(inputs.iloc[end]))
    train = train.batch(batch_size)
    return train

def split_data_option1(inputs, target, batch_size, years):
    start = 0
    end = 1
    current_year = years[start]
    datasets = []
    while (end < len(inputs)):
        while (end < len(inputs)) and (years[end] == current_year):
            end = end + 1
        if (end < len(inputs)):
            current_year = years[end]
        datasets.append(create_data_from_indexes(inputs, target, start, end - 1, batch_size))
        start = end
        end = end + 24
    return datasets

def split_data_option2(n, inputs, target, batch_size):
    range_gap = math.floor(len(inputs) / n)
    x = range(range_gap, len(inputs), range_gap)
    datasets = []
    start = 0
    for n in x:
        end = n
        datasets.append(create_data_from_indexes(inputs, target, start, end, batch_size))
        start = end
    return datasets

datasets = split_data_option1(traffic_left, target, args.batch_size, traffic_left['year'])
NUM_WORKERS = len(datasets)
""""