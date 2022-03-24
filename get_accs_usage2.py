#!/usr/bin/env python3

from rucio.client import Client
from rucio.client.accountclient import AccountClient
from rucio.client.ruleclient import RuleClient
from rucio.client.lockclient import LockClient
from pprint import pprint

rclient = Client()
accclient = AccountClient()

MY_RSE='UNI-BONN_LOCALGROUPDISK'

rulclient = RuleClient()
all_rules = list(rulclient.list_replication_rules({'rse_expression': 'UNI-BONN_LOCALGROUPDISK'}))

lockclient = LockClient()
all_locks = list(lockclient.get_dataset_locks_by_rse(MY_RSE))

temp_rules = set()
perm_rules = set()
for A in range(0, len(all_rules)):
	if all_rules[A]['expires_at'] is None:
		perm_rules.add(all_rules[A]['id'])
	else:
		temp_rules.add(all_rules[A]['id'])

#for A in range(0, len(all_rules)):
#	pprint(all_rules[A])

used_storage = {}
perm_data = {}
temp_data = {}
for A in range(0, len(all_locks)):
	this_acc = all_locks[A]['account']
	this_bytes = all_locks[A]['bytes']
	if this_bytes is None:
		#pprint(all_locks[A])
		continue
	if this_acc not in used_storage:
		used_storage[this_acc] = 0
	used_storage[this_acc] += this_bytes
	rule_id = all_locks[A]['rule_id']
	if rule_id is None:
		print("No rule ID!")
		pprint(all_locks[A])
		continue
	if this_acc not in perm_data:
		perm_data[this_acc] = 0
	if this_acc not in temp_data:
		temp_data[this_acc] = 0
	if rule_id in perm_rules:
		perm_data[this_acc] += this_bytes
	elif rule_id in temp_rules:
		temp_data[this_acc] += this_bytes
	else:
		#print("Rule not found!")
		#pprint(all_locks[A])
		continue
	#r_data = next((r_data for r_data in all_rules if r_data["id"] == rule_id), None)
	#if r_data is None:
	#	print("Rule not found!")
	#	pprint(all_locks[A])
	#	continue
	#if r_data['expires_at'] is None:
	#	if this_acc in perm_data:
	#		perm_data[this_acc] += this_bytes
	#	else:
	#		perm_data[this_acc] = this_bytes
	#else:
	#	if this_acc in temp_data:
	#		temp_data[this_acc] += this_bytes
	#	else:
	#		temp_data[this_acc] = this_bytes
	#if A % 100 == 0:
	#	print("At ",A," of ",len(all_locks),"...")

print("name","mail","bytes total","bytes permanent","bytes temporary",sep="\t")
for acc in used_storage:
	#pprint(accclient.get_account(acc))
	acc_info = accclient.get_account(acc)
	print(acc_info['account'], acc_info['email'], used_storage[acc], perm_data[acc], temp_data[acc], sep="\t")
