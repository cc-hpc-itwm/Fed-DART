#Helper file for ssh connections, not core part of DART
from sshconfig import SSHConfig

def parse_ssh_config(file_obj):
    """
    Provided only as a backward-compatible wrapper around `.SSHConfig`.
    """
    config = SSHConfig()
    config.parse(file_obj)
    return config


def lookup_ssh_host_config(hostname, config):
    """
    Provided only as a backward-compatible wrapper around `.SSHConfig`.
    """
    return config.lookup(hostname)


def get_port_dictionary(config_path):
    #p="/home/SSD/.ssh/ssh_config"
    f = open(config_path, "r")
    c = parse_ssh_config(f)

    hosts=[]
    for h in c.get_hostnames():
        if h != '*':
            host= lookup_ssh_host_config(h, c)
            hosts.append((h, host['port']))

    unique_ports = set()
    for dic in hosts:
        unique_ports.add(dic[1])

    port_dictionary={}
    for port in unique_ports:
        new = []
        for host in hosts:
            if int(host[1]) == int(port):
                new.append(host[0])
        port_dictionary[port] = new

    return port_dictionary