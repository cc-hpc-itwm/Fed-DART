import sys
import time
import json
import binascii
import pickle

sys.path.insert (0, '../python/')

import dart

client = dart.client('https://127.0.0.1:7777', '000') # 000 is the client key (unused atm)

if client.get_job_status('count_words_job') == dart.job_status.unknown:
  client.add_job('count_words_job',
    'count_words_worker',
    'count_words')
  
client.add_tasks('count_words_job', [
  { 'location':'worker#name-:0', 'parameter': '/home/luca/test/test.txt'},
  { 'location':'worker#name-:0', 'parameter': '/home/luca/test/test1.txt'},
  { 'location':'worker#name-:0', 'parameter': '/home/luca/test/test2.txt'},
  { 'location':'worker#name-:0', 'parameter': '/home/luca/test/test3.txt'}])

time.sleep(4);

results = client.get_job_results('count_words_job', 10)
print(results)
for r in results['results']:
  if r['success']:
    print(pickle.loads (binascii.a2b_base64 (r['success'])))