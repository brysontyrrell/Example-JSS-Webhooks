#!/bin/sh
# This example file only reads and prints out the contents of the saved XML from script_runner.php
# Use this as a starting point for a full script to parse the XML and take action on the event

# An optional path to output log entries as shown below
log_path='/tmp/script_runner.log'

# Read the contents of the temporary file with the XML data
data=$(cat $1)

echo "Running my script" >> $log_path
if [ "$data" ]; then
    # Only execute this block if the $data has contents
    echo "Contents of body:" >> $log_path
    echo "$data" >> $log_path
else
    # Execute this block if $data is empty
    echo "Body not found!" >> $log_path
fi

exit 0
