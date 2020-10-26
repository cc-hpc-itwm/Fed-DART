import os
import socket
#TODO: Remove this file and integrate the functions somewhere else
HOME=os.path.expanduser("~")
HOST=socket.gethostname()

JOBID=""
if os.environ.get('SLURM_JOBID') is not None:
    JOBID = os.environ['SLURM_JOBID']

carme_ssh_path = HOME + "/.local/share/carme/job/" + JOBID + "/ssh"

def get_ssh_config_path():
    path = carme_ssh_path + "/ssh_config"
    if not os.path.exists(path):
        return ""
    return path

def get_ssh_public_key():
    path = carme_ssh_path + "/id_rsa_"+JOBID+".pub"
    if not os.path.exists(path):
        return HOME+"/.ssh/id_rsa.pub"
    return path

def get_ssh_private_key():
    path = carme_ssh_path + "/id_rsa_"+JOBID
    if not os.path.exists(path):
        return HOME+"/.ssh/id_rsa"
    return path