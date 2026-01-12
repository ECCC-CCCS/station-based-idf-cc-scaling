'''
Simple function for setting up an SSH connection that can then be used for remote commanding a remote machine and/or SCPing files back and forth (and probably other stuff too, see paramiko docs)\

Example use:
ssh = createSSHClient(REMOVE_SERVER_URL, REMOTE_PORT_THIS_OFTEN_22, USER_NAME_ON_REMOTE, PASSWORD)
scp = SCPClient(ssh.get_transport())

#example1
scp.put(LOCAL_FILE_NAME_WITH_FULL_PATH,REMOTE_FILE_NAME_WITH_FULL_PATH)

#example2
scp.put(LOCAL_DIRECTORY_WITH_ABSOLUTE_PATH,recursive=True,remote_path=WHERE_TO_PUT_ON_REMOTE_SERVER) #careful with remote_path, if this path already exists or not

#example3
scp.get... #sort of the same as the scp.put syntax, see paramiko or StackOverflow for more examples

#example4
(stdin, stdout, stderr)=ssh.exec_command('ls '+REMOTE_SERVER_DIRECTORY_FULL_PATH)
for line in stdout.readlines():
        print(line)
'''

import os
import paramiko
from scp import SCPClient
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

