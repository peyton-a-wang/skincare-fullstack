#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 nnn"
    echo "deletes uploads/nnn.* and deletes the entry in picfile and picblob"
    exit
fi

nnn=$1
rm uploads/$nnn.*
mysql -e "delete from picfile where uid = $nnn;"
