from feddartClient.feddart.messageTranslatorClient import feddart
import random
import numpy as np
from sklearn.cluster import KMeans 

def random_points_generator():
    random_points = [ [random.gauss(0,1), random.gauss(2, 1)] for i in range(15)]
    return np.array(random_points)

@feddart
def init(init_var):
    """ An init task is optional and is executed before
        the first learning task. This task is automatically
        send to all devices, such that the end user mustn't 
        keep this point in mind. 
        Important: variable name (here: init_var) must have
        the same name as defined in the InitTask!!!
    """
    pass

@feddart
def local_k_means(global_centroids, local_iterations):
    random_points = random_points_generator()
    kmeans = KMeans( n_clusters = len(global_centroids)
                   , n_init = 1
                   , init = global_centroids 
                   , max_iter = local_iterations
                   )
    kmeans.fit(random_points)
    return kmeans.cluster_centers_