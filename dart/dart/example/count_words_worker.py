import time
import sys
import json

import binascii
import pickle

def count_words (filename):

  wordCounter = {}       
    
  with open (filename, "r+") as file:
    for word in file.read().split():
      if word not in wordCounter:
        wordCounter[word] = 1
      else:
        wordCounter[word] += 1

  return binascii.b2a_base64 (pickle.dumps (wordCounter))