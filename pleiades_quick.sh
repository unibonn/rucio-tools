#!/bin/bash
# Auth would require: --cacert $X509_USER_PROXY --cert $X509_USER_PROXY
curl -s --capath /etc/grid-security/certificates "https://rucio-hadoop.cern.ch/datasets_per_rse?rse=UNI-BONN_LOCALGROUPDISK" | \
	sort -k4 | \
	awk '{SUM_TOT[$4]+=$5;if ($8 != "\"\"") {SUM_TMP[$4]+=$5} else {SUM_PST[$4]+=$5}} END { for (ACC in SUM_TOT) { printf("%s;%.3f;%.3f;%.3f\n",ACC,SUM_TOT[ACC]/1000/1000/1000/1000,SUM_PST[ACC]/1000/1000/1000/1000,SUM_TMP[ACC]/1000/1000/1000/1000) } }' | \
	LC_ALL=C sort -t ';' -k2,2 -g -r | \
	column -s ';' -t -N 'Accounts,Space total,Space persistent,Space temporary'
