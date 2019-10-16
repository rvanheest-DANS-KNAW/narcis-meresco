#!/bin/sh

NAME=sitemapper
PIDFILE=/home/meresco/meresco/$NAME.pid
LOG=/var/log/narcisindex/$NAME.log

if [ -f $PIDFILE ]
then
    echo "Found PID file. Trying to stop process and delete PID file."

        PID=`cat $PIDFILE 2>/dev/null`
        echo "Shutting down $NAME: $PID"
        echo "Shutting down $NAME: $PID" >> $LOG
        kill $PID 2>/dev/null
        sleep 2
        kill -9 $PID 2>/dev/null
        rm -f $PIDFILE
        echo "STOPPED ${NAME} sitemapper, pid=$PID, `date`"
        echo "STOPPED ${NAME} sitemapper, pid=$PID, `date`" >> $LOG
fi


#nohup sh -c "exec nice ${RUN_CMD} 1>> ${LOG} 2>&1" >/dev/null &
LANG=en_US.UTF-8
export LANG

# START sitemapper on production only, NOT on worker/slave.
STARTMAPPER=narcis*

if [[ "$HOSTNAME" == ${STARTMAPPER} ]]
    then
        sleep 20
        cd /home/meresco/meresco/narcisindex/util
        nohup sh -c "exec ionice -c3 /usr/bin/python ./sitemapper.py 1>> ${LOG} 2>&1" >/dev/null &
        PID=$!
                echo $PID > $PIDFILE
                echo "STARTED ${NAME} sitemapper, pid=$PID, `date`"
                echo "STARTED ${NAME} sitemapper, pid=$PID, `date`" >> $LOG
        echo "STARTING sitemapper, host: "$HOSTNAME" is: "${STARTMAPPER}
    else echo "Not starting sitemapper, host: "$HOSTNAME" is not: "${STARTMAPPER}
fi
# End starting sitemapper

#Crontab:
#@reboot . /etc/profile; /home/meresco/meresco/narcisindex/scripts/start_sitemapper.sh > cron_start_sitemapper.log 2>&1