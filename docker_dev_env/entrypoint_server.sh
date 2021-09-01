#!/bin/sh
sudo -u ubuntu ssh-keygen -t rsa -N "" -f /home/ubuntu/.ssh/id_rsa 
sudo ssh-keygen -A
sudo mkdir /public_key/
touch /home/ubuntu/.ssh/authorized_keys && cat /home/ubuntu/.ssh/id_rsa.pub > /home/ubuntu/.ssh/authorized_keys
sudo cp /home/ubuntu/.ssh/id_rsa.pub /public_key/
cd /home/ubuntu/Fed-DART/dart/dart/bin
sudo service ssh start
sudo -u ubuntu './dart-server.exe'