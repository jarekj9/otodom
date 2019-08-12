#!/bin/bash
cd /home/pi/skrypty/otodom2/
python otodom-getdata.py
python otodom-zabawa.py > otodom-zabawa.txt
python otodom-ftp.py


