#!/bin/sh
mpstat | awk 'NR==4 { print $12 }';
free | awk 'NR==2 { print $7 }';
df / --output='avail' | tail -n 1;
uname -r | cut -d '-' -f 1;
echo '';
apt list --upgradeable 2>/dev/null | awk -F/ 'NR > 1 { print $1 }';
