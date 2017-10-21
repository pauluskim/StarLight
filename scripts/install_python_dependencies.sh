#!/usr/bin/env bash
apt update
apt-get install python-mysqldb
apt-get install python-pip python-dev build-essential 
pip install --upgrade pip
pip install -r /home/ubuntu/StarLight/starlight/requirements.txt
