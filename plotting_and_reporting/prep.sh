#!/bin/sh
pip3 install --upgrade pip
pip3 install -U scipy numpy pandas matplotlib seaborn docopt
echo "prepped" > .prepped.txt
