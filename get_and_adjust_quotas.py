#!/usr/bin/env python
from __future__ import print_function
from multiprocessing import Pool
from rucio.client import Client
from rucio.client.accountclient import AccountClient
from rucio.client.accountlimitclient import AccountLimitClient

import getopt
import sys

rclient = Client()
accclient = AccountClient()
acclimitclient = AccountLimitClient()

def bytes_to_floored_tb(space):
	return space//(1000*1000*1000*1000)
def tb_to_bytes(space):
	return space*1000*1000*1000*1000

MY_RSE = 'UNI-BONN_LOCALGROUPDISK'
MY_DEF_QUOTA = 10*1000*1000*1000*1000
MY_ADM_DEF_QUOTA = 50*1000*1000*1000*1000
DEF_IN_TB = bytes_to_floored_tb(MY_DEF_QUOTA)

BREATHE_SPACE_TB=5
STEP_SPACE_TB=10

def get_usage(acc):
	usage = list(accclient.get_local_account_usage(acc['account'], MY_RSE))
	if usage:
		return usage[0]
	else:
		return {}
def print_help():
	print("Usage:")
	print("--dry-run dry run, don't change any quota.")
	print("-v        increase verbosity.")

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hvd",["dry-run"])
	except getopt.GetoptError:
		print("Argument error!")
		print_help()
		sys.exit(2)

	VERBOSE=False
	DRY_RUN=False

	for opt, arg in opts:
		if opt == "-h":
			print_help()
			sys.exit()
		elif opt == "-v":
			VERBOSE=True
		elif opt in ("-d", "--dry-run"):
			DRY_RUN=True

	pool = Pool(24)

	print("Now checking and adjusting quota of normal DE-cloud users for RSE",MY_RSE,"...")

	accdict = list(accclient.list_accounts(filters={'country-de' : 'user'}))
	res = pool.map(get_usage, accdict)

	for A in range(0,len(accdict)):
		limit = accclient.get_local_account_limit(accdict[A]['account'], MY_RSE)
		cur_quota = limit[MY_RSE]
		#usage = list(accclient.get_local_account_usage(accdict[A]['account'], MY_RSE))
		#cur_usage = 0
		#if usage:
		#	cur_usage = usage[0]['bytes']
		#else:
		#	print("ERROR: Usage query failed for account",accdict[A]['account'],", skipping that!")
		#	continue
		cur_usage = res[A]['bytes']
		if cur_quota==0:
			print("ERROR: Limit for account",accdict[A]['account'],"is zero!")
		quota_to_set=MY_DEF_QUOTA
		usage_in_tb=bytes_to_floored_tb(cur_usage)
		if (cur_usage+tb_to_bytes(BREATHE_SPACE_TB))>MY_DEF_QUOTA:
			quota_to_set = tb_to_bytes(((usage_in_tb+BREATHE_SPACE_TB)//STEP_SPACE_TB+1)*STEP_SPACE_TB)
			if VERBOSE:
				print("Usage for account",accdict[A]['account'],"(with breathe of",BREATHE_SPACE_TB,"TB) larger than default quota:",usage_in_tb,"TB","+",BREATHE_SPACE_TB,"TB",">",DEF_IN_TB,"TB")
				print("  Rounding up for",accdict[A]['account'],"to quota of",bytes_to_floored_tb(quota_to_set),"TB")
			if (cur_quota==quota_to_set):
				if VERBOSE:
					print("  Already set, nothing to adjust!")
					print("")
				continue
		else:
			if cur_quota!=MY_DEF_QUOTA:
				print("Usage for account",accdict[A]['account'],"smaller than default quota, adjusting quota.")
		if (quota_to_set != cur_quota):
			print("  Adjusting quota for account",accdict[A]['account'],"from",bytes_to_floored_tb(cur_quota),"TB to",bytes_to_floored_tb(quota_to_set),"TB...")
			if DRY_RUN:
				print("Not actually doing that since we are asked to do a DRY RUN, ignore the error that setting failed.")
			else:
				acclimitclient.set_local_account_limit(accdict[A]['account'], MY_RSE, quota_to_set)
			new_limit = accclient.get_local_account_limit(accdict[A]['account'], MY_RSE)
			new_quota = new_limit[MY_RSE]
			if quota_to_set!=new_quota:
				print("ERROR: Quota to set:",bytes_to_floored_tb(quota_to_set),"TB, quota found after adjustment:",bytes_to_floored_tb(new_quota),"TB!")
			else:
				print("  Successfully set quota.")
			print("")

	print("Done with normal DE-cloud users!")
	print("")

	print("Now checking and adjusting quota of admin DE-cloud users for RSE",MY_RSE,"...")

	accdict_adm = list(accclient.list_accounts(filters={'country-de' : 'admin'}))
	res_adm = pool.map(get_usage, accdict_adm)

	for A in range(0,len(accdict_adm)):
		limit = accclient.get_local_account_limit(accdict_adm[A]['account'], MY_RSE)
		cur_quota = limit[MY_RSE]
		if cur_quota<MY_ADM_DEF_QUOTA:
			print("Quota for admin account",accdict_adm[A]['account'],"is",bytes_to_floored_tb(cur_quota),"TB which is smaller than default admin quota of",bytes_to_floored_tb(MY_ADM_DEF_QUOTA),"TB, adjusting quota.")
			if DRY_RUN:
				print("Not actually doing that since we are asked to do a DRY RUN, ignore the error that setting failed.")
			else:
				acclimitclient.set_local_account_limit(accdict_adm[A]['account'], MY_RSE, MY_ADM_DEF_QUOTA)
			new_limit = accclient.get_local_account_limit(accdict_adm[A]['account'], MY_RSE)
			new_quota = new_limit[MY_RSE]
			if MY_ADM_DEF_QUOTA!=new_quota:
				print("ERROR: Could not set quota of:",bytes_to_floored_tb(MY_ADM_DEF_QUOTA),"TB, quota found after adjustment:",bytes_to_floored_tb(new_quota),"TB!")
			else:
				print("Successfully set quota.")
			print("")

	print("Done with admin DE-cloud users!")
	print("")


if __name__ == "__main__":
	main(sys.argv[1:])
