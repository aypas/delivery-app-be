from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import sys, os, django, base64, logging
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'delivery_app.settings')
django.setup()
from business_logic.models import Node

logging.basicConfig(filename='scraper.log', filemode='a', 
					level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s @ %(funcName)s from module %(module)s')


class GmailApi:
	def __init__(self, test=False):
		
		self.sources = [['delivery.com'], ['chownow.com'], ['grubhub.com'],
						['toasttab.com'], ['brandibble'],['gloriafood.com']]

		self.emails_by_source = {'delivery.com': [], 'grubhub.com': [],
								 'chownow.com': [], 'gloriafood.com': [],
								 'brandibble': [], 'toasttab.com': [],
								 'unknown': []}

		if not test:
			self.credentials = self.creds()
			self.get_message_bods()
	
	def creds(self):
		nodes, ret = Node.objects.all().filter(pk=1).values('oauth', 'id'), list()
		for i in nodes:
			if i['oauth'] == None:
				continue
			f = i['oauth']
			credentials = Credentials(token=f['token'], refresh_token=f['refresh_token'],
							   		  id_token=f['id_token'], token_uri=f['token_uri'],
							  		  client_id=f['client_id'], client_secret=f['client_secret'],
							 		  scopes=f['scopes'])
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

			n = 0
			for i in result['messages']:
				n+=1
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
			print(n)

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
			extends = [{**l,'source': i[0]} for l in self.emails_by_source[i[0]]]
			ret.extend(extends)
		return ret

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



def make_test_dirs():
	try:
		emails = GmailApi()
		for key in emails.emails_by_source.keys():
			if not os.path.exists('./html/'+key):
				os.makedirs('./html/'+key)
			for i in emails.emails_by_source[key]:
				name = i["email_id"]
				with open("./html/"+key+"/"+name+".html", "w+") as file:
					file.write(str(i['body']))
	except Exception as e:
		print(f"error {e} happened, dont think the function worked.")

if __name__ == "__main__":
	if sys.argv[1] == "make-test-dirs":
		make_test_dirs()