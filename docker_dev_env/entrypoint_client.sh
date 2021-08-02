#!/bin/sh
sudo -u ubuntu ssh-keygen -t rsa -N "" -f /home/ubuntu/.ssh/id_rsa
sudo ssh-keygen -A
touch /home/ubuntu/.ssh/authorized_keys && cat /home/ubuntu/.ssh/id_rsa.pub > /home/ubuntu/.ssh/authorized_keys
cat /public_key_server/id_rsa.pub > /home/ubuntu/.ssh/authorized_keys
sudo service ssh start
python3 start_worker.py "https://${server_ip}:7777" ${client_name}
tail -f /dev/null
