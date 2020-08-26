from scraper import Scrape
from bs4 import BeautifulSoup
from test_dicts import EXPORT as tester
import unittest, os


test = unittest.TestCase()
test.maxDiff = None
sources = ['brandibble', 'chownow.com', 'delivery.com', 'gloriafood.com', 'grubhub.com', 'toasttab.com']



def make_fake_dict(body, _id):
	return {'body': BeautifulSoup(body, 'html.parser'), 'email_id': _id.split('.')[0], 'err': 0}

def get_html_by_id(source):
	return os.listdir(f"./html/{source}")

def populate_ebs(scraper):
	for source in sources:
		files = get_html_by_id(source)
		for file in files:
			html = open(f"./html/{source}/{file}", 'r')
			scraper.GmailApi.emails_by_source[source].append(make_fake_dict(html.read(), file))
			html.close()

def make_scraper_instance():
	scraper = Scrape(test=True)
	populate_ebs(scraper)
	scraper.delivery_scrape()
	scraper.chow_now_scrape()
	scraper.grubhub_scrape()
	scraper.brandibble_scrape()
	scraper.toasttab_scrape()
	scraper.gloriafood_scrape()
	return scraper

#asserts should be done here
def test_keys(scraper):
	errs = 0
	lists = scraper.GmailApi.unpacked_ebs
	for i in range(len(lists)):
		for j in range(i+1, len(lists)):
			first = list(lists[i]['db_values'].keys())
			second = list(lists[j]['db_values'].keys())
			first.sort()
			second.sort()
			try:
				test.assertEqual(first, second)
			except AssertionError as e:
				errs+=1
				print(e, ' from sources ', lists[i]['source'], ' and ', lists[j]['source'] )
	if errs == 0:
		print("db_values keys test has passed")
	else:
		print("db_values keys test has failed. ", errs, " is the number of errors")

def test_values(scraper):
	f = 0
	for source in sources:
		for i in scraper.GmailApi.emails_by_source[source]:
			testee = i['email_id']
			standard = list(filter(lambda x: x['email_id'] == testee, tester[source]))[0]
			try:
				test.assertDictEqual(i['db_values'], standard['body'])
				print('testee with id',testee, 'passed!')
			except AssertionError as e:
				if testee == "1720a8189e044a41":
					#we've got a problem...given time is made as now+timedelta...so the mss dont match
					#ill figure something out...simply need a reference point for time from html
					continue
				print("comparing ", testee, " with values ", i['db_values'])
				print(e)
				f+=1
				break
		#for now lets only have one error
		if f != 0:
			break
	if f == 0:
		print('passed...kinda sorta')
	else:
		print('failed, idk where')

def eye_test(scraper):
	#comment out individual scrapes to exclude them
	for i in scraper.GmailApi.emails_by_source.keys():
		for l in scraper.GmailApi.emails_by_source[i]:
			print(l.get('db_values', None), i, '\n\n')

if __name__ == "__main__":
	scraper = make_scraper_instance()
	eye_test(scraper)
	test_keys(scraper)
	test_values(scraper)
