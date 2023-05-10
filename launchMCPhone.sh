#!/bin/sh
# launchMCPhone.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/chapi/telefon
sudo python TelephoneDaemon.py
cd /