#!/bin/bash

usage="$0 server
	Connect to the specified synergy server, using ssh port
	forwarding.
"

knownIP="
172.30.56. foppl
10.42.43. foppl
192.168.0. portico
"

if [ -z "$1" ]
then
	for ip in `ifconfig | sed -n 's/.*inet addr:\(\([0-9]\{1,3\}\.\)\{3\}\).*/\1/p'`
	do
		while read kip kserv
		do
			if [ "$ip" == "$kip" ]
			then
				server=$kserv
			fi
		done <<< "$knownIP"
	done
	if [ -z "$server" ]
	then
		echo "$usage"
		exit 0
	fi
else
	server=$1
fi
echo $server

# Are these really necessary any more?
xset r 116
xset r 113

#process=`netstat -t4lnp 2> /dev/null | awk 'BEGIN {FS="[ /]*"}; /24800.*ssh/ {print $7}'`
process=`netstat -t4lnp 2> /dev/null | sed -n 's/.*24800.* \([0-9]*\)\/ssh/\1/p'`
# netstat args: t - only TCP
#				4 - only IP4
#				l - only listening ports
#				n - numeric ports
#				p - give process info
if [[ "x$process" != x && "x$server" == "x$(expr match "$(ps -p $process u)" '.* \([a-z]*\)')" ]]
then
	echo "Already connected to $server"
else
	if [ -n "$process" ]
	then
		kill $process
	fi
	ssh -f -N -L 24800:localhost:24800 $server
fi

if ps -C synergyc > /dev/null
then
	echo "Already running synergyc"
else
	synergyc localhost
fi
