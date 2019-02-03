#!/usr/bin/env bash

cd data/11.0
echo "============================================= make 11.0"
./make.sh
cd ../../data/11.0.debug
echo "============================================= make 11.0.debug"
./make.sh
