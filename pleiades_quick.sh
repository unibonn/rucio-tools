#!/bin/bash
curl -s --capath /etc/grid-security/certificates --cacert $X509_USER_PROXY --cert $X509_USER_PROXY "https://rucio-hadoop.cern.ch/datasets_per_rse?rse=UNI-BONN_LOCALGROUPDISK" | \
	sort -k4 | \
	awk '{SUM[$4]+=$5} END { for (ACC in SUM) { printf("%s;%.3f\n",ACC,SUM[ACC]/1000/1000/1000/1000) } }' | \
	LC_ALL=C sort -t ';' -k2,2 -g -r | \
	column -s ';' -t -N 'Accounts,Space'
