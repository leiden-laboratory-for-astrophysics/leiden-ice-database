import paramiko
import getpass

server = 'icedb.strw.leidenuniv.nl'

username = getpass.getuser()

if username == 'vagrant':
  username = input('STRW username: ')
else:
  print('Deploying with user:', username)

password = getpass.getpass()

print('Deploying to %s@%s' % (username, server))

def run(ssh, command):
  (stdin, stdout, stderr) = ssh.exec_command(command)
  for line in stdout.readlines():
    print(line)


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server, username=username, password=password)
run(ssh, 'cd /data/icedb/ice-database; git pull')
run(ssh, 'cd /data/icedb/ice-database; pip install -r requirements.txt')
ssh.close()

print('Finishing deploying to %s@%s' % (username, server))
