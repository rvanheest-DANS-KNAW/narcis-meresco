#!/bin/sh
#

LOG="/var/lib/python-meresco-harvester/log/narcis.harvester.log"

REP=""
if [ "x$1" != "x" ] ; then
    REP=" $1"
fi

RUN_CMD="~/scripts/harvest_narcis_domain.sh${REP}"
echo $RUN_CMD

nohup sh -c "${RUN_CMD} 1>>${LOG} 2>&1" >/dev/null  &
#nohup sh -c "${RUN_CMD}" > /dev/null  &

echo "STARTED ${NAME} meresco-harvester, `date`"