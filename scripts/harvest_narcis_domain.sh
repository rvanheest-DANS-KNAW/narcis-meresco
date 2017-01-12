#!/bin/bash

# Give repository id to harvest just 1 repository

REP=""
if [ "x$1" != "x" ] ; then
    REP="--repository=$1"
fi

#@reboot geeft error, wellicht omdat bepaalde processen er nog niet zijn? Dus we wachten...
sleep 2

# override default 1 hour: set to 2 hours.
#--set-process-timeout=7200

HARVESTONLY=*meresco21*

if [[ "$HOSTNAME" == ${HARVESTONLY} ]]
    then
        while /bin/true; do
            meresco-harvester --domain=narcis --runOnce --set-process-timeout=7200 $REP
            sleep 1800
        done
    else echo "No harvest, host: "$HOSTNAME" is not: "${HARVESTONLY}
fi
