#!/bin/sh

NAME=api-server
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
	echo "STOPPED ${NAME}, pid=$PID, `date`"
	echo "STOPPED ${NAME}, pid=$PID, `date`" >> $LOG    
fi


LANG=en_US.UTF-8
export LANG
nohup sh -c "exec /home/meresco/meresco/narcisindex/bin/start-api --port=8004 --indexPort=8002 --gatewayPort=8000 --stateDir=/data/meresco/api 1>> ${LOG} 2>&1" >/dev/null &
PID=$!
echo $PID > $PIDFILE

echo "STARTED ${NAME}, pid=$PID, `date`"
echo "STARTED ${NAME}, pid=$PID, `date`" >> $LOG