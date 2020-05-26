#!/usr/bin/env python3

from multiprocessing import Pool
from rucio.client import Client
from rucio.client.accountclient import AccountClient
from rucio.client.accountlimitclient import AccountLimitClient

import getopt
import sys

rclient = Client()
accclient = AccountClient()
acclimitclient = AccountLimitClient()

MY_RSE = 'UNI-BONN_LOCALGROUPDISK'

def check_in_cloud(acc):
	is_in_cloud = False
	attrs = list(accclient.list_account_attributes(acc['account']))[0]
	for kv in attrs:
		if (kv['key'] == 'country-de'):
			is_in_cloud = True
			break
	return is_in_cloud

def get_limit(acc):
	limit = accclient.get_local_account_limit(acc['account'], MY_RSE)
	if limit:
		return limit[MY_RSE]
	else:
		return {}

def main(argv):
	pool = Pool(24)

	accdict = list(accclient.list_accounts())
	res_in_cloud = pool.map(check_in_cloud, accdict)
	res_limit = pool.map(get_limit, accdict)

	for A in range(0,len(accdict)):
		#print(accdict[A])
		if res_limit[A]:
			if not res_in_cloud[A]:
				print("Error: Account ",accdict[A]," not in cloud anymore, but still has quota!")
		else:
			if res_in_cloud[A]:
				print("Warning: Account ",accdict[A]," in cloud, but has no quota!")
	print("")

if __name__ == "__main__":
	main(sys.argv[1:])
