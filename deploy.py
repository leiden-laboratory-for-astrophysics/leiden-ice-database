import paramiko
import sys
import getpass

server = 'icedb.strw.leidenuniv.nl'
destiny = '/data/icedb'

username = getpass.getuser()

if username == 'vagrant':
  #username = input('STRW username: ')
  username = 'olsthoorn'
else:
  print('Deploying with user:', username)

password = getpass.getpass()

print('Deploying to %s@%s' % (username, server))

def run(ssh, command):
  print('$', command)
  (stdin, stdout, stderr) = ssh.exec_command(command)
  for line in stdout.readlines():
    sys.stdout.write(line)


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server, username=username, password=password)

# Update source code
run(ssh, 'cd %s/ice-database; git pull' % destiny)

# Update requirements
print('Updating requirements (this might take a while)..')
run(ssh, 'cd %s; pip install -r ice-database/requirements.txt' % destiny)

# Symlink shared files/directories
run(ssh, 'cd %s/ice-database; rm application/config.py' % destiny)
run(ssh, 'cd %s/ice-database; ln -s /data/icedb/shared/config.py application/config.py' % destiny)
run(ssh, 'cd %s/ice-database; rm -rf application/data' % destiny)
run(ssh, 'cd %s/ice-database; ln -s /data/icedb/shared/data application/data' % destiny)

ssh.close()
print('Finished deploying to %s@%s' % (username, server))
