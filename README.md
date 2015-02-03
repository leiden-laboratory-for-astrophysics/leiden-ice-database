# Sackler Laboratory Ice Database
A Python [Flask](http://flask.pocoo.org) project that uses [NumPy](http://www.numpy.org) and [D3.js](http://d3js.org) to show IR spectra of ice.

Setting up a development environment can be a time-consuming process, so this project includes a fully configured Vagrant set-up (read _Development Environment Set-up_ below). It's highly recommended that you use this.

## Development Environment Set-up
### Prerequisites
This project includes a [Vagrant](https://www.vagrantup.com) configuration file that allows you to easily set up a development environment. Vagrant uses [VirtualBox](https://www.virtualbox.org) by default, so also make sure you have that installed.

> Are you using a Leiden Observatory computer? Make sure you set VirtualBox to store its VMs outside your home (~/) directory, because the home folder is limited to 2GB. Open VirtualBox and click `File->Preferences`, then under the `General` tab pick a different `Default Machine Folder`. For example, use `/data1/icemachine` instead.

Also verify you have a Terminal and `git` installed.

### Install machine
Open a terminal and run the following commands and keep on reading.

```bash
git clone https://github.com/bartolsthoorn/ice-database
cd ice-database
vagrant up
```

Vagrant will now install a new Debian machine, including all the requirements for this project (this might take `~15 min`). This is called _provisioning_. Once this is done, connect to the newly made machine with the command below.

> Seeing warnings? The `vagrant up` might show warnings like `default: dpkg-preconfigure: unable to re-open stdin: No such file or directory` and `default: stdin: is not a tty`, and perhaps other warnings. This is usually nothing to worry about and we'll test the set-up later.

> If for any reason the provisioning process fails, it's always possible to run `vagrant provision` again. The provisioning scripts are idempotent, which means that you can run them again without getting into trouble (it checks what's already installed).

```bash
vagrant ssh
```

You should now be connected to the fully configured machine. To make sure everything is installed, run the following commands.

```bash
pyenv versions
cd /vagrant && python --version
python app.py
```

The `/vagrant` folder is a shared folder between the virtual machine and your developer machine.

### Developing
This set-up features a ViM configuration, so you could use this as your editor. This is not at all required though, it's handy to know that the `/vagrant` folder on the virtual machine is actually the same folder as this repository. So you can freely edit the files on your host machine with your favourite editor and just run python / server using the virtual machine.

### Delete machine
To delete a vagrant machine use `vagrant destroy` (this will delete all its data as well). To rebuild use `vagrant up` again.

### Starting the production server
```bash
ssh icedb.strw.leidenuniv.nl
cd /data/icedb/ice-database
gunicorn application:app -b 0.0.0.0:5000 --pid ../gunicorn -D
```
