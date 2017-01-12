#!/bin/sh
#
NAME="meresco-harvester-internal-server"
LOG=~/log/$NAME.log 

# meresco-harvester-internal-server verzorgt door Meresco install.
RUN_CMD="${NAME} --port 8888 --dataPath /var/lib/python-meresco-harvester/data --logPath /var/lib/python-meresco-harvester/log --statePath /var/lib/python-meresco-harvester/state --harvesterStatusUrl https://tmeresco21.dans.knaw.nl/page/showHarvesterStatus/show"

# echo "${RUN_CMD} 1>> ${LOG} 2>&1"

nohup sh -c "${RUN_CMD} 1>> ${LOG} 2>&1" >/dev/null  &

echo "STARTED ${NAME} , `date`"
echo "STARTED ${NAME} , `date`" >> $LOG
