import json
import paramiko
import base64
import getpass
import os.path

file_with_cred = "Hosts"
read_file = open(file_with_cred, mode='r')
act_user = {}
all_user = {}
def_user = getpass.getuser()
for line in read_file:
    line = line.replace('[', ' ').replace(']', ' ').replace('"', '\"')
    line = line.strip('\n')[:-1]
    if line != '':
        act_user = json.loads(line)
        act_user.update({"auth_type": "key"})
        con_serv = paramiko.client.SSHClient()
        con_serv.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        con_serv.load_host_keys(os.path.expanduser('~') + '/.ssh/known_hosts')
        try:
            con_serv.connect(hostname=act_user["hostname"], username=act_user["user"], timeout= 5.0)
            stdin, stdout, stderr = con_serv.exec_command("cd bw/ && git rev-parse --abbrev-ref HEAD")
            stdout.channel.recv_exit_status()
            exit_code = stdout.channel.recv_exit_status()
            if (exit_code == 0):
                act_user.update({"vcs_type": "git"})
                stdout = stdout.readlines()
                act_user.update({"branch": stdout[0].rstrip()})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && git rev-list --count HEAD")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"revision": stdout[0].rstrip()})
            else:
                act_user.update({"vcs_type": "svn"})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && svn info --show-item url")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"branch": stdout[0].rstrip()})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && svn info --show-item revision")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"revision": stdout[0].rstrip()})
                con_serv.close()
            all_user.update({act_user["user"]: act_user})
        except paramiko.ssh_exception.AuthenticationException:
            act_user.update({"auth_type": "password"})
            con_serv.connect(hostname=act_user["hostname"], username=act_user["user"], password=act_user["user"], timeout= 5.0)
            stdin, stdout, stderr = con_serv.exec_command("cd bw/ && git rev-parse --abbrev-ref HEAD")
            stdout.channel.recv_exit_status()
            exit_code = stdout.channel.recv_exit_status()
            if (exit_code == 0):
                act_user.update({"vcs_type": "git"})
                stdout = stdout.readlines()
                act_user.update({"branch": stdout[0].rstrip()})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && git rev-list --count HEAD")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"revision": stdout[0].rstrip()})
            else:
                act_user.update({"vcs_type": "svn"})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && svn info --show-item url")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"branch": stdout[0].rstrip()})
                stdin, stdout, stderr = con_serv.exec_command("cd bw/ && svn info --show-item revision")
                stdout.channel.recv_exit_status()
                stdout = stdout.readlines()
                act_user.update({"revision": stdout[0].rstrip()})
                con_serv.close()
            all_user.update({act_user["user"]: act_user})
        except (EOFError, paramiko.AuthenticationException, socket.error):
            print("Host " + act_user["hostname"] + " недоступен")
output_to_json = open("json_out", mode='w', encoding='utf-8')
json.dump(all_user, output_to_json)
