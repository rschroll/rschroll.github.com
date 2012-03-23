#!/bin/bash

usage="$0

This script concatenates a series of PDF files, leaving out the first page of
all but the first file.  It is designed for joining the sections of a /Numerical
Recipes/ chapter into a single file, as each section shares its first and last 
page with the previous and subsequent section.

	$0 file [ file ... ]
	
Concatenates the listed files, sending the output to stdout.  You probably want
to redirect it."

if [ "$#" -eq 0 ]
then 
	echo "$usage"
	exit 1
fi

if  [ "$#" -gt 26 ]
then
	echo "Due to a limitation in pdftk, this script cannot concatenate more than"
	echo "26 files at a time.  Consider concatenating the files in several steps."
	exit 1
fi

if [ -t 1 ]
then
	echo "This script prints the concatenated file to stdout, which is detected to"
	echo "be a terminal.  Use output redirection (\"> out.pdf\") to save the file."
	exit 1
fi

ALPHA="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cmd="pdftk "
i=0
for f in "$@"
do
	cmd+="${ALPHA:$i:1}=$f "
	let "i += 1"
done
cmd+="cat A "
j=1
while [ "$j" -lt "$i" ]
do
	cmd+="${ALPHA:$j:1}2-end "
	let "j += 1"
done
cmd+="output -"
$cmd
