import sys
import time

sys.path.insert (0, '../python/')

import dart

client = dart.client('https://127.0.0.1:7777', '000') # 000 is the client key (unused atm)

client.add_worker(['127.0.0.1'], 2, 'worker#name-:0', ['local_cluster'], 0)