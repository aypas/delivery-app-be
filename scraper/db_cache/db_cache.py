import threading, time, json, sys, django, os
from datetime import datetime, timezone, timedelta
sys.path.append('../..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'delivery_app.settings')
django.setup()
from business_logic.models import Node, Partner
#when resource is updated(Node or Partner) from view
#call threaded cache w/ updated data to update cache from view concurrently

#files
CACHE = './cache/cache.json'
NU = './cache/node_update.json'
PU = './cache/partner_update.json'

class ManageCache:

	def construct_cache(self):
		#{ nid: {node_name:str, node_pk:int, node_oauth:json, partners: { partner_name(for quick look ups): {  partner_other_names, partner_pk}}}}
		JSON = {'last_updated': str(datetime.now(timezone.utc)), 'cache': {}}
		cache = JSON['cache']
		nodes = Node.objects.all().values('id', 'name')
		for node in nodes:
			#d = {**node, 'partners': {}}
			cache[node['id']] = {**node, 'partners': {}}
			partners = Partner.objects.filter(of_node=node['id']).values('name', 'other_names', 'id', 'of_node')
			for partner in partners:
				cache[node['id']]['partners'][partner['name']]=partner
		with open(CACHE, 'w') as file:
			json.dump(JSON, file)

	def update_cache(self, node, partner):
		with open(CACHE, 'r') as file:
			cache = json.load(file)['cache'] 
		if node[0]:
			#loop through each item looking for a match on id(using binary would be smart...)
			for i in node[1]:
				p=cache[i['id']]['partners']
				cache[i['id']] = {'id': i['id'], 'name':i['name'], 'partners': p }
				
		if partner[0]:
			for i in partner[1]:
				cache[i['of_node']]['partner'][i['name']] = i

		with open(CACHE, 'w') as file:
			json.dump({'last_updated': datetime.now(timezone.utc), 'cache': cache}, file)

	def check_update(self):
		n, p = False, False
		with open(NU, 'r') as file:
			node = json.load(file)
			if bool(node):
				n = True

		with open(PU, 'r') as file:
			partners = json.load(file)
			if bool(partners):
				p = True

		if n or p:
			update([n, node], [p, partner])
			return True
		else:
			return False


	#call within scraper
	#all concurrency that might take place in scraper should happen after this is called
	def check_for_update(self):
		with open(CACHE, 'r') as file:
			JSON = json.load(file)

		#checks if last update/construct was greater than x minutes ago
		if datetime.now(timezone.utc)-datetime.fromisoformat(JSON['last_updated'])>timedelta(minutes=15):
			print('time to reconstruct cache...')
		else:
			self.check_update()



def read_write():
	#basic construct for reading/writing to node.json
	with open('node.json', 'r') as file:
		f = json.load(file)

	with open('node.json', 'w') as file:
		if not f.get('read_count', None):
			f['read_count']=1
		else:
			f['read_count'] += 1
		json.dump(f, file)

class AsyncCacheUpdate(threading.Thread):
	def run(self):
		#kwargs {'node': model_object, 'partner': model_object}
		#needs a file lock...
		print(self._kwargs)
		if self._kwargs['node']:
			with open(NU, 'r') as file:
				f=json.load(file)



if __name__ == '__main__':
	#ManageCache(kwargs={'view_update': True}).start()
	construct_cache()