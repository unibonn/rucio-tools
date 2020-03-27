#!/bin/bash
./get_accs_usage.py | \
	egrep -v '^name' | \
	sort -rn -k4 | \
	awk -vFS=$'\t' 'BEGIN{OFS=","}{print $1, $2, $3, $4/1000/1000/1000/1000, $5/1000/1000/1000/1000}' | \
	column -s, -t -N name,mail,files,size/TB,quota/TB
