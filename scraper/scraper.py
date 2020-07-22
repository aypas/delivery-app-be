from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from scraper_regex import DeliveryHelper, CommonHelper, GloriaHelper, BrandHelper, ToastHelper
import sys, os, django, base64, re, logging
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'delivery_app.settings')
django.setup()
from business_logic.models import Node, Partner, Order

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
		complete = models.BooleanField()
		completed_time = models.DateTimeField()
'''

logging.basicConfig(filename='scraper.log', filemode='a', 
					level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s @ %(funcName)s from module %(module)s')


class Scrape:

	def __init__(self):
		self.credentials = self.creds()
		self.emails_by_source = {'delivery.com': [], 'grubhub.com': [],
								 'chownow.com': [], 'gloriafood.com': [],
								 'brandibble': [], 'toasttab.com': [],
								 'unknown': []}
		self.get_message_bods()
		self.sources = [['delivery.com', self.delivery_scrape], 
						['chownow.com', self.chow_now_scrape],
						['grubhub.com', self.grubhub_scrape],
						['toasttab.com', self.toasttab_scrape],
						['brandibble', self.brandibble_scrape],
						['gloriafood.com', self.gloriafood_scrape]]

	
	def creds(self):
		nodes, ret = Node.objects.all().values('oauth', 'id'), list()
		for i in nodes:
			if i['oauth'] == None:
				continue
			f = i['oauth']
			credentials = Credentials(token=f['token'], refresh_token=f['refresh_token'],
							   		  id_token=f['id_token'], token_uri=f['token_uri'],
							  		  client_id=f['client_id'], client_secret=f['client_secret'],
							 		  scopes=f['scopes'])

			print(credentials.valid)
			if not credentials.valid:
				print('refreshing...')
				credentials.refresh()
				i.oauth["token"] = credentials.token
				i.save()
			ret.append([credentials, i['id']])	
		return ret

	def get_message_bods(self):
		for creds in self.credentials:

			service = build('gmail', 'v1', credentials=creds[0])

			#grabs list of emails matching query parameter
			result = service.users().messages().list(userId='me',q='from:omardoor2door@gmail.com').execute()
			#just realized i need to set q up with email of node...so that must also be added to self.creds
			
			if not result['resultSizeEstimate']:
				continue

			for i in result['messages']:
				email_id = i['id']
				

				f = service.users().messages().get(id=i['id'], userId='me', format='full').execute()
				label_id = f['labelIds']

				payload = f['payload']['parts'][1]['body']['data']
				

				#here, we decode part two(html), part one is weird, don't use it
				body = BeautifulSoup(base64.urlsafe_b64decode(payload).decode('utf-8'), 'html.parser')

				#here we turn the bytes object to a string and append to a dict/list to be returned
				self.find_source({'email_id': email_id, 'body': body,
							 	  'creds': creds[0], 'node_id': creds[1], 
							 	  'labels': f['labelIds'], 'err': 0})

	def find_source(self, email_details):
			
		soup = email_details['body']

		f=str(soup.blockquote)

		if 'delivery.com' in f:
			self.emails_by_source['delivery.com'].append(email_details)
		elif 'chownow.com' in f:
			self.emails_by_source['chownow.com'].append(email_details)
		elif 'grubhub.com' in f:
			self.emails_by_source['grubhub.com'].append(email_details)
		elif 'gloriafood.com' in f:
			self.emails_by_source['gloriafood.com'].append(email_details)
		elif 'brandibble' in f:
			self.emails_by_source['brandibble'].append(email_details)
		elif 'toasttab.com' in f:
			self.emails_by_source['toasttab.com'].append(email_details)
		else:
			logging.warning("email found with unknown source")
			self.emails_by_source['unknown'].append(email_details)
		return None

	@property
	def unpacked_ebs(self):
		ret = list()
		for i in self.sources:
			ret.extend(self.emails_by_source[i[0]])
		return ret
	
	def delivery_scrape(self, retry=False, jobs=None):
		emails = jobs if retry else self.emails_by_source['delivery.com']

		for email in emails:
			try:
				soup = email['body']
				order_num_and_partner= soup.find('td', colspan='3')

				#both vals are retrieved
				order_num = DeliveryHelper.strip_order(order_num_and_partner.span.string)
				partner = order_num_and_partner.contents[0].strip()
				#return values is 'Order#[0-9]' gotta strip with CleanData

				#deliver_by
				deliver_by = soup.find('td', colspan='4').span.text



				#get customer's name, address, special instructions, order time, and phone#
				customer_data = soup.find('tr', id='CUSTOMER-INFO-AND-SPECIAL-INSTRUCTIONS')
				customer_info = DeliveryHelper.customer_info(''.join(customer_data.strings).splitlines())

				#all vars are added to dict
				ret = {'order_number':order_num or '', 'partner': partner or '',
					   'deliver_by': deliver_by, 'note': '', **customer_info}#FIX DELIVERY BY!!!

				#print(ret)
				#i might need to pay someone to figure this one out...address is rough...



				#get delivery fee, tip, total, and maybe discount(talk to almir about how that works)
				#bs4 grabs data in bottom right of page
				labels = list(soup.find('td', id="MERCHANT-RECEIVES-LABELS").strings)
				values = list(soup.find('td', id="MERCHANT-RECEIVES-VALUES").strings)

				#zip values and labels
				for i,j in zip(labels, values):
					
					if ' '.join(i.split())=='Delivery fee:':
						ret['delivery_fee'] = DeliveryHelper.strip_float(j) or ''
					elif ' '.join(i.split())=='Tip:':
						ret['tip'] = DeliveryHelper.strip_float(j) or ''
					elif ' '.join(i.split())=='Merchant receives:':
						ret['total_price'] = DeliveryHelper.strip_float(j) or ''

					#add db values to dict
				
				email['db_values'] = ret
			except Exception as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue

		return None

	def grubhub_scrape(self, retry=False, jobs=None):
		emails = jobs if retry else self.emails_by_source['grubhub.com']
		for email in emails:
			try:
				soup = email['body']

				#html = str(soup.find_all('blockquote', attrs={'type': 'cite'})[1]) #oooooooooo

				#retreival of partner and name is simple, only two calls
				partner = soup.find('div', attrs={'data-field':'restaurant-name'}).text
				name = soup.find('div', attrs={'style': 'color:#000;font-family:Roboto,sans-serif;font-size:14px;line-height:16px;margin-top:0'}).text
				order_id = ''.join(soup.find_all('span', attrs={'style': 'font-weight:700'})[1].strings)
				#print(order_id)

				order_data = soup.find('div', attrs={'data-section':"order"})
				tip = order_data.find('div', attrs={'data-field':'tip'}).text
				fee = order_data.find('div', attrs={'data-field':'delivery-charge'}).text
				total = order_data.find('div', attrs={'data-field':'total'}).text

				deliver_by = soup.find('div', attrs={'style':'color:#000;font-family:Roboto,sans-serif;font-size:18px;line-height:17px;margin:10px;margin-top:4px;margin-left:31px;font-weight:700; '})
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
									  'delivery_fee':CommonHelper.strip_float(fee) or '',
									  'tip':CommonHelper.strip_float(tip) or '',
									  'total_price':CommonHelper.strip_float(total) or '',
									  'deliver_by':deliver_by or '',
									  'note': note}
			except Exception as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue

		return None

		#grubhub scrape is almost perfect!!!
		#only problem is, apartment number doesnt fit into address perfectly

		#and also, having the actual order number would be good for almir probably(currently, order # is order id)

	def chow_now_scrape(self, retry=False, jobs=None):
		#deliver by does not work...
		emails = jobs if retry else self.emails_by_source['chownow.com']
		for email in emails:
			try:
				soup = email['body']

				#html = str(soup.find_all('blockquote', attrs={'type': 'cite'})[1]) #oooooooooo


				order_num = CommonHelper.strip_order(soup.find('h1', attrs={'bgcolor': '#efefef'}).span.text) or ''

				#doc[0] has rest details, doc[1] has customer details, doc[2] has $$$
				doc = soup.find_all('div', attrs={'class':'two-columns'})

				#rest details
				partner = doc[0].span.text.split('-')[0].rstrip() or ''


				#customer details
				customer_name, customer_phone, address, delivery_time = str(), str(), str(), str()
				for i in doc[1].find_all('div'):
					label = i.label
					if label:
						if label.text == 'Customer Name':
							customer_name = i.find('span').text
						elif label.text == 'Customer Phone Number':
							customer_phone = i.find('span').text

						elif label.text == 'Customer Address':
							i.label.decompose()
							#print(i)
							address = re.sub(r"\n|\r|\s+"," ",i.find('span').text).strip()

						elif label.text == 'Time Of Order':
							pass
							#print(i.text)
						elif label.text == 'Requested Delivery Time':
							i.label.decompose()
							deliver_by = i.text


				email['db_values'] = {'partner': partner, 'order_number':order_num,
									  'customer_phone': customer_phone, 'address': address,
									  'customer_name': customer_name, #'deliver_by': deliver_by,
									  'note': ''}

				#Order Details
				order_deets = doc[2].find_all('tbody')[1]
				trs = order_deets.find_all('tr')

				for i in trs:
					text = i.text.splitlines()

					if text[1]=='Delivery Fee:':
						email['db_values']['delivery_fee'] = CommonHelper.strip_float(text[2]) or ''
					elif text[1]=='Tip/gratuity:':
						email['db_values']['tip'] = CommonHelper.strip_float(text[2]) or ''
					elif text[1]=='Grand Total:':
						email['db_values']['total_price'] = CommonHelper.strip_float(text[2]) or ''
			except Exception as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue
		return None

	def gloriafood_scrape(self, retry=False, jobs=None):
		emails = jobs if retry else self.emails_by_source['gloriafood.com']
		for email in emails:
			try:
				soup = email['body'].find('table', attrs={'class': 'templateContainer'})
				main = soup.select('td#bodyCell > table > tbody > tr')

				order_num, rname = GloriaHelper.ordern_and_rname(main[1].find('h1').text)
				deliver_time = main[2].find('td', attrs={"class": "mcnTextContent"}).select("div > span > span > table")
				index = GloriaHelper.date_time(deliver_time[0].text.splitlines())
				if index != None:
					delivery_time = deliver_time[index]
				else: 
					delivery_time = 'unknown'

				customer = main[2].find('td', attrs={'class': "mcnBoxedTextContentColumn"})
				name_phone_addr = customer.span.text.splitlines()
				kw = GloriaHelper.name_phone_addr(name_phone_addr)
				note = customer.find_all('strong')[-1].text.split(':')[1]

				prices = GloriaHelper.scrape_prices(soup.find('table', attrs={'class': "mcnTextContent"}).find_all('td'))

				email['db_values'] = {**kw, **prices, 'note': note, 'deliver_by': delivery_time,
					   				  'order_number': order_num, 'partner': rname.strip()}

				#problem 1: sometimes delivery by is just minutes...gotta make that work
				#problem 2: i should probably use datetime objects for all time fields
			except Exception as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue

	def brandibble_scrape(self, retry=False, jobs=None):
		emails = jobs if retry else self.emails_by_source['brandibble']
		for email in emails:
			try:
				soup = email['body']
				s = soup.find_all("table", attrs={"class": "container"})[0].select("tbody > tr > td > table")[1].select("tr")
				details = BrandHelper.customer_and_rest(s[1].find_all('p'))
				prices = BrandHelper.prices(s[2].find_all('p'))
				email['db_values'] = {**details, **prices}
			except Exception as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue

	def toasttab_scrape(self, retry=False, jobs=None):
		emails = jobs if retry else self.emails_by_source['toasttab.com']
		for email in emails:
			try:
				soup = email['body']
				soup_major = soup.find_all('blockquote')[1]\
						.select('table > tbody')[0]\
						.find_all('table')[1].select('tbody')[0]


				order_number = ToastHelper.order(soup_major.find('strong'))
				customer_and_prices = soup_major.select('table')[0].select('tr')
				c_and_p = ToastHelper.customer(customer_and_prices)
				email['db_values'] = {'order_number': order_number, **c_and_p}
			except Exeption as e:
				if email['err'] == 0:
					logging.error(str(e)+f" error with {email['email_id']} id @")
				email['err']+=1
				continue

	def error_retry(self):
		for i in self.sources:
			err_scrape = list(filter(lambda email: email['err'] == 1, self.emails_by_source[i[0]])) 
			if err_scrape:
				self.i[1](retry=True, jobs=err_scrape)

	def save_to_database(self):
		'''
			saves messages scraped with a non fail result to DB
		'''
		try:
			bulk = list()
			for source in self.sources:
				for data in self.emails_by_source[source[0]]:
					if data['err']!=0:
						result = "something went wrong"
					else:
						result = 'success'
					print(data['node_id'], data['db_values']['partner'])
					partner = Partner.objects.all().filter(of_node_id=data['node_id'])\
											       .filter(name__contains=data['db_values']['partner'])[0]
					bulk.append(Order(store=partner,html=data['body'].find_all('blockquote')[1], assigned_to=None,
									  result=result, source=source[0],
									  customer_phone=data['db_values']['customer_phone'],
									  order_number=data['db_values']['order_number'],
									  name=data['db_values']['customer_name'], 
									  address=data['db_values']['address'],
									  deliver_by=data['db_values']['deliver_by'],
									  total_price=data['db_values']['total_price'],
									  tip=data['db_values']['tip'],
									  delivery_fee=data['db_values']['delivery_fee'],
									  note=data['db_values']['note']))

			Order.objects.bulk_create(bulk)
			return True
		except Exception as e:
			print(e)
			logging.error(str(e)+f"...this is very very bad @ ")
			return False

	def gmail_labels(self):
		'''
		this method modifies the succesfully scraped messages
		so that they no longer have an unread label, 
		and will no longer be retrieved on __init__

		the fucked up thing here is that no token is ever refreshed...
		'''
		print('running labs')
		labels={'addLabelIds':[], 'removeLabelIds':['UNREAD']}
		emails = self.unpacked_ebs
		for i in self.creds():
			node_emails = list(filter(lambda x: i[1]==x['node_id'], emails))
			if not node_emails:
				continue
			service = build('gmail', 'v1',credentials=i[0])

			for email in node_emails:		
				service.users().messages().modify(userId='me', id=email['email_id'],
											   	  body=labels).execute()

	
	def unread(self):
		'''
		changes label of read email to unread
		this method is for test purposes only.
		'''
		service = build('gmail', 'v1', credentials=self.credentials[0][0])
		for email in self.unpacked_ebs:
			labels={'addLabelIds':['UNREAD'], 'removeLabelIds':[]}
			result = service.users().messages().modify(userId='me', id=email['email_id'],
										   	 		   body=labels).execute()

	@staticmethod
	def do_scrape():
		'''
		method to run all must need methods
		'''
		try:
			scrape = Scrape()
			print('scrape happened')
			scrape.delivery_scrape()
			print('delivery works')
			scrape.grubhub_scrape()
			print('grub works')
			scrape.chow_now_scrape()
			scrape.brandibble_scrape()
			scrape.toasttab_scrape()
			scrape.gloriafood_scrape()
			print('495')
			scrape.error_retry()
			# if not scrape.save_to_database():
			# 	scrape.gmail_labels()
			# 	print('ran labels')
			# else:
			# 	print('labels didnt work')
			# 	pass
			return scrape
		except Exception as e:
			print(e)
			logging.error(str(e)+f" ")



if __name__ == '__main__':
	#Scrape.do_scrape()
	print(10)