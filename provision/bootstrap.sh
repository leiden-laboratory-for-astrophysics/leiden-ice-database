#!/usr/bin/env bash

# Provisioning script by Bart Olsthoorn
# olsthoorn@strw.leidenuniv.nl / bartolsthoorn@gmail.com

apt-get update
apt-get upgrade

apt-get install -y zsh vim git tmux build-essential libssl-dev libbz2-dev \
    zlib1g-dev libreadline-dev libsqlite3-dev wget curl llvm htop \
    libhdf5-serial-dev cmake unzip
apt-get build-dep -y matplotlib

# Continue provisioning with Vagrant user rights
su vagrant -l -c 'source /vagrant/provision/vagrant.sh'

# Change default shell to ZSH
chsh -s /bin/zsh vagrant

#wget http://python-distribute.org/distribute_setup.py
#python distribute_setup.py
#easy_install pip
#pip install flask
