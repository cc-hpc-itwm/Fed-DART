#!/bin/sh
echo "killing proc drts-kernel"
kill $(ps aux | grep 'drts-kernel' | grep -v grep | grep -v ssh | awk '{ print $2 }' | tr '\n' ' ') 2>/dev/null &
wait