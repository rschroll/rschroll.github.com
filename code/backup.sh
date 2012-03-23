#!/bin/bash
# Make backups of the home directories

# Configuration options
# The location at which the backups will be mounted.  Right now, is just
# the default location at which Ubuntu mounts external disks.  Perhaps we
# should set up /etc/fstab to mount to backup drive somewhere special.
BASEBACK=/media/backup
# If this file exists in each user's home directory, it will be passed to
# rsync as --exclude-from.  File names that match a pattern within this file
# will be excluded from the backup.  For the syntax, see the "Include/Exclude
# Pattern Rules" section of the rsync man page.
IGNOREFILE=.backup.ignore

if [ "$(id -u)" != "0" ]
then
	echo "Only root has the permissions necessary to create a backup."
	echo "Run the command: sudo $0"
	exit 1
fi

if [ "$(mount | grep $BASEBACK | wc -l)" != "1" ]
then
	echo "Expecting backup drive to be mounted at $BASEBACK"
	echo "Please mount drive before continuing."
	exit 1
fi

f=($BASEBACK/[0-9]*/)	# Get only directories; glob will sort them for us
LASTBACK=${f[@]:(-1)}	# Who says shell notation is obtuse?
CURBACK="$BASEBACK/`date +%Y%m%d`/"
RSYNCCMD="rsync -a --link-dest=$LASTBACK"

if [ "$LASTBACK" = "$CURBACK" ]
then
	echo "$CURBACK already exists.  Have you already made a backup today?"
	echo "This script only supports one backup per day.  If you absolutely must"
	echo "have a backup right now, (re)move $CURBACK"
	exit 1
fi

cd /home
# Using extened globs in bash - match everything except lost+found
# May need to turn on with shopt -s extglob
shopt -s extglob
for dir in !(lost+found)
do
	if [ -e "$dir/$IGNOREFILE" ]
	then
		CMD="$RSYNCCMD --exclude-from=$dir/$IGNOREFILE"
	else
		CMD=$RSYNCCMD
	fi
	
	$CMD $dir $CURBACK
done
		
