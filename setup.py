from setuptools import setup

setup( name = 'FedDart'
     , version = '0.1'
     , description = 'Python library for federated machine learning'
     , author = 'ITWM'
     , author_email ='nico.weber@itwm.fraunhofer.de'
     , packages = ['feddart']
     , install_requires = [ "dill"
                          , "requests"
                          ]
     )