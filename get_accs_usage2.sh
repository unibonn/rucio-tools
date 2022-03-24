#!/bin/bash
./get_accs_usage2.py | \
	egrep -v '^name' | \
	sort -rn -k2 | \
	awk -vFS=$'\t' 'BEGIN{OFS=","}{print $1, $2, $3/1000/1000/1000/1000, $4/1000/1000/1000/1000, $5/1000/1000/1000/1000}' | \
	column -s, -t -N name,mail,size/TB,perm/TB,temp/TB
