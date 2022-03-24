#!/usr/bin/env python3

from multiprocessing import Pool
from rucio.client import Client
from rucio.client.accountclient import AccountClient

rclient = Client()
accclient = AccountClient()

MY_RSE='UNI-BONN_LOCALGROUPDISK'

def get_usage(acc):
	usage = list(accclient.get_local_account_usage(acc['account'], MY_RSE))
	if usage:
		return usage[0]
	else:
		return {}

pool = Pool(24)

accdict = list(accclient.list_accounts(filters={'country-de' : 'user'})) + list(accclient.list_accounts(filters={'country-de' : 'admin'}))
res = pool.map(get_usage, accdict)

print("name","mail","files","bytes","limit",sep="\t")
for A in range(0,len(accdict)):
	if res[A] and res[A]['bytes']!=0:
		limit = accclient.get_local_account_limit(accdict[A]['account'], MY_RSE)
		print(accdict[A]['account'],accdict[A]['email'],res[A]['files'],res[A]['bytes'],limit[MY_RSE],sep="\t")
		#identities = list(accclient.list_identities(accdict[A]['account']))
		#for ident in range(0,len(identities)):
		#	if ident == 0:
		#		print(accdict[A]['account'],identities[ident]['email'],identities[ident]['identity'],res[A]['files'],res[A]['bytes'],sep="\t")
		#	else:
		#		print("",identities[ident]['email'],identities[ident]['identity'],"","",sep="\t")
