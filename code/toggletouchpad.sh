#!/bin/bash

prop=`xinput list-props "SynPS/2 Synaptics TouchPad" | grep "Device Enabled"`
enable=$(((${prop: -1} + 1) % 2))
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Device Enabled" 8 $enable
