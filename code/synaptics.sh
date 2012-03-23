#!/bin/sh
#
# Use xinput --list-props "SynPS/2 Synaptics TouchPad" to extract data
#
# http://blog.mfabrik.com/2009/10/11/setting-up-multi-touch-scrolling-for-ubuntu-9-10-karmic-koala-linux-on-asus-eee-1005ha-netbook/

# Set multi-touch emulation parameters
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Synaptics Two-Finger Pressure" 32 10
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Synaptics Two-Finger Width" 32 8
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Two-Finger Scrolling" 8 1
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Synaptics Two-Finger Scrolling" 8 1 1

# Disable edge scrolling
#xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Synaptics Edge Scrolling" 8 0 0 0 

# This will make cursor not to jump if you have two fingers on the touchpad and you list one
# (which you usually do after two-finger scrolling)
xinput set-int-prop "SynPS/2 Synaptics TouchPad" "Synaptics Jumpy Cursor Threshold" 32 110

# Make 2 finger tap be middle button.  Maybe also with xinput "Synaptics Tap Action"
synclient TapButton2=2
synclient TapButton3=3
