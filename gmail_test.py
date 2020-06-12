import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE","delivery_app.settings")
django.setup()

from business_logic.models import Node, Partner, Order
from django.db import IntegrityError

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from bs4 import BeautifulSoup

import base64
import re




class CleanData:

	@classmethod
	def strip_float(cls, val):
		ret = ''
		for i in val:
			if i.isdigit():
				ret += i
			else:
				if i=='.':
					ret += i
		return float(ret)

	@classmethod
	def strip_string(cls, val):
		pass

	@classmethod
	def strip_phone_num(cls, val):
		#MUST have bs4 strings object passed as val to work
		for i in val:
			if re.match(r"^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", i):
				return i

	@classmethod
	def strip_name(cls, val):
		'''
			works for delivery.com...very shitily done method

			must be fed a bs4 strings object that has been .join()'d
			AND .striplines()'d
		'''
		for i in val:
			if i != '':
				return i, val.index(i)

	@classmethod
	def strip_address(cls, val):
		'''
			at the end of all addresses is one zip code!

			like strip, val must be a bs4 string object
			that's been join'd AND striplines'd
		'''

		pass

	@classmethod
	def is_zipcode(cls,val,loop=None,start_index=0):
		#start index is optional
		#there are too many goddamn loops in this thing...lets minimize the looping
		if not loop:
			return re.match(r"^\d{5}(-\d{4})?$", val)!=None

		for i in val[start_index:]:
			if re.match(r"^\d{5}(-\d{4})?$",i[-5:]) or re.match(r"^\d{5}(-\d{4})?$",i[-10:]):
				return True, val.index(i)

		return False, 'FAIL' 

	@classmethod
	def strip_order(cls, val):
		return re.sub("[^0-9]", "", val)



'''
node fields:
		owner = models.OneToOneField()
		managers = models.ManyToManyField() 
		address = models.CharField()
		code = models.IntegerField()
		oauth = JSONField()

order fields:

		--store = models.ForeignKey()
		assigned_to = models.ForeignKey()
		--html = models.TextField()
		--result = models.CharField()
		--source = models.CharField()
		--customer_phone=models.CharField()
		--order_number = models.CharField()
		--name = models.CharField()
		--address = models.CharField()
		--deliver_by = models.CharField()
		--entry_date = models.DateTimeField()	
		--total_price = models.DecimalField()
		--tip = models.DecimalField()
		--delivery_fee = models.DecimalField()
		--note = models.CharField()
		in_progress = models.BooleanField()
		--complete = models.BooleanField()
		completed_time = models.DateTimeField()
'''


def get_message_body():
	vals = []
	f = Node.objects.all()[0].oauth

	creds = Credentials(token=f['token'],refresh_token=f['refresh_token'],
						id_token=f['id_token'],token_uri=f['token_uri'],
						client_id=f['client_id'],client_secret=f['client_secret'],
						scopes=f['scopes'])

	#tokens never expire and I don't know why

	service = build('gmail', 'v1', credentials=creds)

	#grabs list of emails matching query parameter
	result = service.users().messages().list(userId='me',q='from:almirdoor2door@gmail.com').execute()



	#loops through list of messages; current query yields 3; 
	#result['messages']=[{id:email_id, thread_id:idk what this is tbh}, ... ]...one dict for each email
	for i in result['messages']:
		email_id = i['id']
		#grabs email data of email with i['id'] of emails
		f = service.users().messages().get(id=i['id'], userId='me', format='full').execute()

		#response is gigantic and borderline impossible to navigate. Need to map out each response dict
		'''
				for delivery.com f[payload][parts] returns list of messages broken into parts(?)(more on that later)
				body of message to be decrypted is f[payload][parts][0][body][data]/f[payload][parts][1][body][data]

				this format might be the same across all emails where mimeType='text/plain

				delivery.com's mimeType is text/plain....i think
		'''

		payload = f['payload']['parts'][1]['body']['data']
		

		#here, we decode part two(html), part one is weird, don't use it
		body = base64.urlsafe_b64decode(payload)

		#here we turn the bytes object to a string and append to a dict/list to be returned
		vals.append({'email_id': email_id, 'body': body.decode('utf-8')})

	return vals




#the above function works for grubhub, delivery.com, and ChowNow
#(two of these companies i didnt know existed before 10/15/19, lmao)

#which reminds me, I should add source of order to db.




class Scrape:

	def __init__(self):
		self.credentials = self.creds()
		self.vals = self.get_message_bods()

	def __repr__(self):
	    return '<%s.%s object at %s>' % (self.__class__.__module__,
	        							 self.__class__.__name__,
	        							 hex(id(self)))


	
	def creds(self):
		nodes, ret = Node.objects.all(), list()
		for i in nodes:
			f=i.oauth
			ret.append([Credentials(token=f['token'], refresh_token=f['refresh_token'],
							    id_token=f['id_token'], token_uri=f['token_uri'],
							    client_id=f['client_id'], client_secret=f['client_secret'],
							    scopes=f['scopes']),
				   i.pk])	

	def get_message_bods(self):
		vals = []

		for creds in self.creds:

			service = build('gmail', 'v1', credentials=creds[0])

			#grabs list of emails matching query parameter
			result = service.users().messages().list(userId='me',q='from:almirdoor2door@gmail.com').execute()
			#just realized i need to set q up with email of node...so that must also be added to self.creds
			
			if not result['resultSizeEstimate']:
				break

			for i in result['messages']:
				email_id = i['id']
				

				f = service.users().messages().get(id=i['id'], userId='me', format='full').execute()
				label_id = f['labelIds']

				payload = f['payload']['parts'][1]['body']['data']
				

				#here, we decode part two(html), part one is weird, don't use it
				body = base64.urlsafe_b64decode(payload)

				#here we turn the bytes object to a string and append to a dict/list to be returned
				vals.append({'email_id': email_id, 'body': body.decode('utf-8'),
							 'creds': creds[0], 'node_id': creds[1], 'labels': f['labelIds']})

		return vals

	def find_source(self):

		for i in self.vals:
			
			soup = BeautifulSoup(i['body'],'html.parser')

			f=soup.blockquote

			if 'delivery.com' in str(f):
				i['source'] = 'delivery.com'
			elif 'ChowNow' in str(f):
				i['source'] = 'ChowNow'
			elif 'grubhub.com' in str(f):
				i['source'] = 'grubhub.com'
			else:
				print('wtf')
				i['source'] = ''
				#this cf should trigger an sms warning to node owners
		return None

	#all three methods below should return the db values
	#from their respective html formats

	
	def delivery_scrape(self):
		#i need deliver by, forgot about it

		#i cannot do note, as in the only example i have, there is no note

		body = self.vals

		work = list(filter(lambda x: x['source']=='delivery.com', body))

		if not work:
			return None

		for email in work:
			
			#instantiate bs4
			soup = BeautifulSoup(email['body'], 'html.parser')

			
			html = str(soup.find_all('blockquote', attrs={'type': 'cite'})[1]) #ooooooo
			#order number, and partner are inside the below object
			order_num_and_partner= soup.find('td', colspan='3')

			#both vals are retrieved
			order_num = CleanData.strip_order(order_num_and_partner.span.string)
			partner = order_num_and_partner.contents[0].strip()
			#return values is 'Order#[0-9]' gotta strip with CleanData

			#deliver_by
			deliver_by = soup.find('td', colspan='4').span.text



			#get customer's name, address, special instructions, order time, and phone#
			customer_data = soup.find('tr', id='CUSTOMER-INFO-AND-SPECIAL-INSTRUCTIONS')
			customer_data_arg = ''.join(list(customer_data.strings)).splitlines()
			#always remember, strings atribute returns generator


			customer_phone = CleanData.strip_phone_num(customer_data.strings) #Works!
			customer_name, __index = CleanData.strip_name(customer_data_arg) #i forget why i return index with strip


			#i have a really clever aproach to this fucked up logic on a note inside the car...i should implement it, as it is this is fucked
			__, index = CleanData.is_zipcode(customer_data_arg, loop='yes')
			
			address = customer_data_arg[index-1]+customer_data_arg[index]


			#all vars are added to dict
			ret = {'order_number':order_num or '', 'partner': partner or '',
				   'customer_phone': customer_phone or '', 'address': address or '',
				   'customer_name':customer_name or '', 'deliver_by': deliver_by, 'note': '',
				   'html': html}#FIX DELIVERY BY!!!

			
			#i might need to pay someone to figure this one out...address is rough...



			#get delivery fee, tip, total, and maybe discount(talk to almir about how that works)
			#bs4 grabs data in bottom right of page
			labels = list(soup.find('td', id="MERCHANT-RECEIVES-LABELS").strings)
			values = list(soup.find('td', id="MERCHANT-RECEIVES-VALUES").strings)

			#zip values and labels
			for i,j in zip(labels, values):
				
				if ' '.join(i.split())=='Delivery fee:':
					ret['delivery_fee'] = CleanData.strip_float(j) or ''
				elif ' '.join(i.split())=='Tip:':
					ret['tip'] = CleanData.strip_float(j) or ''
				elif ' '.join(i.split())=='Merchant receives:':
					ret['total_price'] = CleanData.strip_float(j) or ''

				#add db values to dict
			
			email['db_values'] = ret

		return None
			#order # is in need of CleanData method

			#THIS METHOD IS FRAIL BECAUSE IF ADDRESS IS CONTAINED INSIDE 3 LINES
			#ADRESS WONT BE RETRIEVED IN WHOLE
			#AND
			#IF NOTE EXISTS, NEW CONDITIONAL STATEMENTS WILL BE NEEDED

			#needs lots of testing also in need of different iterations of delivery.com template

	def grubhub_scrape(self):
		#forgot deliver by
		
		body = self.vals
		ret = dict()
		work = list(filter(lambda x: x['source']=='grubhub.com', body))

		if not work:
			return None
		
		for email in work:
			soup = BeautifulSoup(email['body'],'html.parser')

			html = str(soup.find_all('blockquote', attrs={'type': 'cite'})[1]) #oooooooooo

			#retreival of partner and name is simple, only two calls
			partner = soup.find('div', attrs={'data-field':'restaurant-name'}).text
			name = soup.find('div', attrs={'style': 'color:#000;font-family:Roboto,sans-serif;font-size:14px;line-height:16px;margin-top:0'}).text

			


			order_data = soup.find('div', attrs={'data-section':"order"})

			order_id = order_data.find('div', attrs={'data-field':'order-id'}).text
			tip = order_data.find('div', attrs={'data-field':'tip'}).text
			fee = order_data.find('div', attrs={'data-field':'delivery-charge'}).text
			total = order_data.find('div', attrs={'data-field':'total'}).text

			deliver_by = soup.find('div', attrs={'style':'color:#000;font-family:Roboto,sans-serif;font-size:15px;line-height:17px;margin:10px;margin-top:4px'})
			deliver_by = deliver_by.text.split('  ')[2].strip()



			diner = soup.find('div', attrs={'data-section':'diner'})

			address = ''
			customer_phone = ''
			note = ''

			#its 2:30 am, this loop is bad
			#ill figure out a way to get rid of it later...or maybe keep it
			for i in diner:
				try:
					
					if 'address' in i.attrs['data-field']:
						address += i.text

					elif i.attrs['data-field'] == 'phone':
						customer_phone = i.text.strip()

					elif i.attrs['data-field'] == 'special-instructions':
						note = i.text

					elif i.attrs['data-field'] == 'city':
						address += i.text+', '

					elif i.attrs['data-field'] == 'state':
						address += i.text+', '

					elif i.attrs['data-field'] == 'zip':
						address += i.text					

				except:
					pass

			
			email['db_values'] = {'order_number':order_id or '','partner':partner or '',
								  'address': address or '', 'customer_name': name or '',
								  'customer_phone': customer_phone or '', 'note': note or '',
								  'delivery_fee':CleanData.strip_float(fee) or '',
								  'tip':CleanData.strip_float(tip) or '',
								  'total_price':CleanData.strip_float(total) or '',
								  'deliver_by':deliver_by or '',
								  'note': note, 'html': html}

		return None

		#grubhub scrape is almost perfect!!!
		#only problem is, apartment number doesnt fit into address perfectly

		#and also, having the actual order number would be good for almir probably(currently, order # is order id)

	def chow_now_scrape(self):
		#i cannot do note, as the only example email i have has no note!!!
		body = self.vals
		work = list(filter(lambda x: x['source']=='ChowNow', body))

		if not work:
			return None
		

		for email in work:

			soup = BeautifulSoup(email['body'],'html.parser')

			html = str(soup.find_all('blockquote', attrs={'type': 'cite'})[1]) #oooooooooo


			order_num = CleanData.strip_order(soup.find('h1', attrs={'bgcolor': '#efefef'}).span.text) or ''

			#doc[0] has rest details, doc[1] has customer details, doc[2] has $$$
			doc = soup.find_all('div', attrs={'class':'two-columns'})

			#rest details
			partner = doc[0].span.text.split('-')[0].rstrip() or ''



			#customer details
			doc1_divs = doc[1].find_all('div', attrs={'class':'left'})


			deliver_by = ' '.join(doc1_divs[1].text.replace('Requested Delivery Time','').split())
			customer_name = doc1_divs[2].span.text or ''
			customer_phone = doc1_divs[3].span.text or ''
			

			#below is address, which is the one div
			#in doc[1] that has no class set
			address = doc[1].find('div', attrs={'class':None}).text
			address = ' '.join(address.split()).replace('Customer Address','').lstrip() or ''


			
			email['db_values'] = {'partner': partner, 'order_number':order_num,
								  'customer_phone': customer_phone, 'address': address,
								  'customer_name': customer_name, 'deliver_by': deliver_by,
								  'note': '', 'html': html}


			#Order Details
			order_deets = doc[2].find_all('tbody')[1]
			trs = order_deets.find_all('tr')

			for i in trs:
				text = i.text.splitlines()

				if text[1]=='Delivery Fee:':
					email['db_values']['delivery_fee'] = CleanData.strip_float(text[2]) or ''
				elif text[1]=='Tip/gratuity:':
					email['db_values']['tip'] = CleanData.strip_float(text[2]) or ''
				elif text[1]=='Grand Total:':
					email['db_values']['total_price'] = CleanData.strip_float(text[2]) or ''

		return None

	def results(self):
		'''
		adds result key to self.vals['db_values'];

		if all data is truthy, result=success
		if the only falsey valued data is note, result=success

		if critical data is missing(anything but note), 
		result is probable error, body will be saved to db, 
		so that a manager can manually enter data
		'''
		for data in self.vals:

			if all(list(data['db_values'].values())):
				data['db_values']['result'] = 'Success'
				
			else:
				values_list = [data['db_values'][i] for i in list(data['db_values'].keys()) if i!='note']
				if not data['source']:
					#send sms
					#this means this email has no identifiable source, and therefore cannot be scraped,
					#the email must be marked as read by the node owner, otherwise the app will be slowed down

					#the problem with an sms error code is i only want it to be sent once...
					#but it might be sent like once every minute for an entire hour

					#a new key in data is made because a self.vals dict with no source does not have db_values
					data['Error'] = True
		
				elif all(values_list):
					data['db_values']['result'] = 'Success'

				else:
					data['db_values']['result'] = 'Probable Error' 
					#means manager should manually check data validity



	def save_to_database(self):
		'''
			saves messages scraped with a non fail result to DB
		'''
		for data in self.vals:
			if data.get('source', None):
									

				try:
					partner = Partner.objects.all().filter(of_node_partner=data['node_id'])\
										     .filter(name__contains=data['db_values']['partner'])[0]

					Order.objects.create(store=partner,html=data['db_values']['html'], assigned_to=None,
										 result=data['db_values']['result'], source=data['source'],
										 customer_phone=data['db_values']['customer_phone'],
										 order_number=data['db_values']['order_number'],
										 name=data['db_values']['customer_name'], 
										 address=data['db_values']['address'],
										 deliver_by=data['db_values']['deliver_by'],
										 total_price=data['db_values']['total_price'],
										 tip=data['db_values']['tip'],
										 delivery_fee=data['db_values']['delivery_fee'],
										 note=data['db_values']['note'])
				except Exception as o:
					print(o,'cock')
				




	def gmail_labels(self):
		'''
		this method modifies the succesfully scraped messages
		so that they no longer have an unread label, 
		and will no longer be retrieved on __init__
		'''
		
		for i in self.creds():
			emails = filter(lambda x: i[1]==x['node_id'], self.vals)
			service = build('gmail', 'v1',credentials=i[0])

			for email in self.vals:

				if email['source'] and email['db_values']['result'] != 'Error':
					labels={'addLabelIds':[], 'removeLabelIds':['UNREAD']}
					service.users().messages().modify(userId='me', id=email['email_id'],
												   	  body=labels).execute()

	
	def unread(self):
		'''
		changes label of read email to unread
		this method is for test purposes only.
		'''
		service = build('gmail', 'v1',credentials=list(self.credentials)[0][0])
		for email in self.vals:
			labels={'addLabelIds':['UNREAD'], 'removeLabelIds':[]}
			result = service.users().messages().modify(userId='me', id=email['email_id'],
										   	 		   body=labels).execute()

	@staticmethod
	def do_scrape():
		'''
		method to run all must need methods
		'''
		
		scrape = Scrape()
	
		scrape.find_source()
		scrape.delivery_scrape()
		scrape.grubhub_scrape()
		scrape.chow_now_scrape()
		scrape.results()
		#scrape.save_to_database()
		scrape.gmail_labels()

		return scrape



if __name__ == '__main__':
	scrape = Scrape()

	scrape.do_scrape()
	#unread() might cause confusion in future tests
	#the thing of it is, in get_message_bods(), in production,
	#q must filter is:unread
	#so unread wont work through self.vals
	#if q='...is:unread', as it won't have any messages to make unread.
	#in order to change to unread
	#ye must delete is:unread from q
	#so that unread can get the read messages to make unread


	#at this point, the only thing preventing this thing being production ready
	#is the fact that i only have three template examples

	#especially for delivery.com, i need more...

	#also create a data display on order_details...the html copy works great tho!!!