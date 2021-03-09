import unittest
import os
import sys
import numpy as np
d = os.path.dirname(os.getcwd())
sys.path.append(d + '/genetic_algorithms')


class TestCellBody(unittest.TestCase):

    def setUp(self):
        self.dict_cells_specification = { "window_factor": "no"
                                        , "cells": [ { "layer_initialization": []
                                                     , "maximal_width_of_cell": 4
                                                     , "maximal_depth_of_cell": 22 
                                                     , "maximal_level_back": 10
                                                     , "min_active_layer_in_cell": 5
                                                     , "max_active_layer_in_cell": 30
                                                     , "search_space": ["dummy"]
                                                     , "mutable": "yes"
                                                     , "residual_connections_to_cells": []
                                                     }
                                                   ]
                                        }
        self.layerlist = [ {"name":'Layertype01', "type":'dummy', "inputs": 1, 'tags': 'hello'}
                         , {"name":"Layertype02", "type":"dummy", "inputs": 1, 'tags': 'hello'}
                         , {"name":"Layertype03", "type":"dummy", "inputs": 1, 'tags': 'hello'}
                         ]
        self.input_shape = [10,2]

    def tearDown(self):
        pass

    def test_immutable_cellbody(self):
        """Build an immutable CellBody without a search space."""
        dict_cells_specification = { "window_factor": "no"
                                   , "cells": [ { "layer_initialization": []
                                                , "maximal_width_of_cell": 4
                                                , "maximal_depth_of_cell": 22 
                                                , "maximal_level_back": 10
                                                , "min_active_layer_in_cell": 5
                                                , "max_active_layer_in_cell": 30
                                                , "search_space": []
                                                , "mutable": "no"
                                                , "residual_connections_to_cells": []
                                                }
                                              ]
                                    }
        cellbody = CellBody(dict_cells_specification, self.layerlist, self.input_shape)
        self.assertTrue( isinstance(cellbody, CellBody)
                       , msg = "Failed to build a cellbody instance!"
                       )
    

if __name__ == '__main__':
    unittest.main(verbosity = 2)
