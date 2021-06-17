#!/bin/bash

function paired_devices() {
  {
    printf "select $adapter\n\n"
    printf "paired-devices\n\n"
  } | bluetoothctl | grep "Device " | sed -r 's/^.*(([0-9A-F]{2}:){5}[0-9A-F]{2}).*$/\1/'
}

function is_connected() {
  {
    printf "select $adapter\n\n"
    printf "info $device\n\n"
  } | bluetoothctl | grep "Connected: " | sed -e 's/Connected: //' | sed -e 's/^[[:blank:]]*//'
}

bluetoothctl -- list | while read line
do
  adapter=`echo $line | sed -r 's/^.*(([0-9A-F]{2}:){5}[0-9A-F]{2}).*$/\1/'`

  paired_devices | while read device
  do
    if [[ $(is_connected) = "no" ]]; then
      {
        printf "select $adapter\n\n"
        printf "connect $device\n\n"
      } | bluetoothctl
    fi
  done
done

