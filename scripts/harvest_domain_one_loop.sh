#!/bin/bash

# Give domain to harvest. Just 1 loop.

DOM=" "
if [ "x$1" != "x" ] ; then
    DOM="--domain=$1"
fi

meresco-harvester $DOM
#/var/lib/python-merescoharvester/startharvester.py $DOM