import re, pytz
from datetime import datetime, timedelta
import datetime as dt

eastern = pytz.timezone('US/Eastern')
#all this needs desperate fixing
class CommonHelper:

	@staticmethod
	def strip_float(val):
		ret = ''
		for i in val:
			if i.isdigit():
				ret += i
			else:
				if i=='.':
					ret += i
		return float(ret)

	@staticmethod
	def strip_string(val):
		pass

	@staticmethod
	def strip_phone_num(val):
		for i in val:
			if re.match(r"((\(\d{3}\) ?)|(\d{3}-))?\d{3}-\d{4}", i):
				return i
		return None

	@staticmethod
	def strip_name(val):
		'''
			works for delivery.com...very shitily done method

			must be fed a bs4 strings object that has been .join()'d
			AND .striplines()'d
		'''
		for i in val:
			if i != '':
				return i, val.index(i)

	@staticmethod
	def strip_address(val):
		'''
			at the end of all addresses is one zip code!

			like strip, val must be a bs4 string object
			that's been join'd AND striplines'd
		'''

		pass

	@staticmethod
	def is_zipcode(val, start_index=0):

		for i in range(start_index, len(val)):
			if re.match(r"^\d{5}(-\d{4})?$",val[i][-5:]) or re.match(r"^\d{5}(-\d{4})?$",val[i][-10:]):
				return True, i
		return False, 0 

	@staticmethod
	def strip_order(val):
		return re.sub("[^0-9]", "", val)

	@staticmethod
	def float(val):
		r"^\$[0-9]+(\.[0-9][0-9])?$"


	@staticmethod
	def match_time(val):
		e=re.compile(r"^(.*?)([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])\s*([AaPp][Mm])")
		re.match(e, val)


class DeliveryHelper(CommonHelper):
	'''
	customer name is always first not None in val
	'new customer' or 'returning customer' is always second
	next not None val is beggining of address, zip_code index is end, anything 
	in between is part of address
	'''
	@staticmethod
	def customer_info(val):
		for i in range(len(val)):
			if val[i]:
				name = val[i]
				name_index = i
				break
		b, index = CommonHelper.is_zipcode(val, start_index=name_index+1)
		phone_num, note = str(), str()
		for i in range(len(val)):
			if val[i] == "SPECIAL INSTRUCTIONS:":
				note = ''.join(val[i+1:-1]).strip()
		if not b:
			address = 'pickup'
		else:
			address = val[index-1]+val[index]
			if CommonHelper.strip_phone_num([val[index+1]])!=None:
				phone_num = val[index+1]
		if not phone_num:
			phone_num = CommonHelper.strip_phone_num(val)

		return {'customer_phone': phone_num,
				'address': address,
				'customer_name': name,
				'note': note}

class GrubHubHelper:

	@staticmethod
	def deliver_by(data):
		return eastern.localize(datetime.strptime(data, "%B %d, %Y, %I:%M %p")).astimezone(pytz.utc)

class GloriaHelper(CommonHelper):

	@staticmethod
	def ordern_and_rname(val):
		t = val.split('-')
		return CommonHelper.strip_order(t[1]), t[0]

	@staticmethod
	def date_time(val):
		for i in val:
			if "minutes" in i:
				return (datetime.now()+timedelta(minutes=int(i.strip()[:2]))).astimezone(pytz.utc)
			if "day" in i:
				return eastern.localize(datetime.strptime(i.strip(),"%A, %B %d, %Y, %I:%M %p")).astimezone(pytz.utc)

	@staticmethod
	def name_phone_addr(val):
		name, phone, addr = str(), str(), str()
		#print(val)
		for i in val:
			if i:
				name = i
				break
			name = 'sheeeit'

		for i in val:
			if re.match(r"^\+|(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", i):
			 	#print(i)
			 	phone=i
			 	break
		addr = val[-1]
		return {'customer_name': name,
				'customer_phone': phone,
				'address': addr}


	@staticmethod
	def scrape_prices(val):
		total = float()
		tip = float()
		delivery_fee = float()
		for i in range(len(val)):
			if 'TOTAL'==val[i].text:
				total = CommonHelper.strip_float(val[i+1].text)
			elif 'DELIVERY FEE' == val[i].text:
				delivery_fee = CommonHelper.strip_float(val[i+1].text)
			elif 'TIP:' == val[i].text:
				tip = CommonHelper.strip_float(val[i+1].text)

		return {'total_price': total,
				'tip': tip,
				'delivery_fee': delivery_fee}


class BrandHelper(CommonHelper):
	@staticmethod
	def date_time(time):
		if 'between' in time:
			print('started')
			t1 = re.findall(r"((([1-9]|[012])\:([0-5][0-9]))(AM|PM))", time)[1][0]
			print(t1)
			t = datetime.strptime(t1, "%I:%M%p")
			return eastern.localize(datetime.combine(datetime.now().date(), t.time())).astimezone(pytz.utc)

		elif 'about' in time:

			indexes = re.search(r"(([1-9]|[012])\:([0-5][0-9]))\s(AM|PM)", time).span()
			tt = datetime.strptime(time[indexes[0]:indexes[1]], "%I:%M %p")
			print(tt, time)
			return eastern.localize(datetime.combine(datetime.now().date(), tt.time())).astimezone(pytz.utc)
	@staticmethod
	def customer_and_rest(val):
		name, address, phone_num, order_id, partner, deliver_by = str(), str(), str(), str(), str(), str()
		order_type = str()
		for i in val:
			t = i.text.split(':', 1)

			if t[0] == 'Address':
				text = t[1].splitlines()
				name = text[1].strip()
				address = ''.join(text[2:]).strip()
				#print(address, 'hellooooo\n')
			elif t[0] == 'Phone':
				phone_num = t[1].strip()
			elif t[0] == 'Order ID':
				order_id = t[1].strip()
			elif 'Store' == t[0]:
				partner = t[1].strip()
			elif 'Notes for Store' == t[0]:
				note = t[1].strip()
			elif 'Requested Time' == t[0]:
				#theres one email with between x and y
				#another with 'by about x'
				#there might be other formats tho
				deliver_by = BrandHelper.date_time(t[1])
			elif 'Order Type' == t[0]:
				if t[1].strip()=='Pick-Up':
					address = str()
					order_type == 'pick-up'
				else:
					order_type = 'delivery'

		return {'customer_name': name,
				'address': address,
				'customer_phone': phone_num,
				'order_number': order_id,
				'partner': partner,
				'deliver_by': deliver_by,
				'note': note}

	@staticmethod
	def prices(val):
		tip, d_fee, total = float(), float(), float()
		for i in val:
			t = i.text.splitlines()
			if t[1] == 'Gratuity':
				tip = CommonHelper.strip_float(t[2])
			elif 'Total' in t[1]:
				total = CommonHelper.strip_float(t[2])
			elif 'Delivery Fee' in t[1]:
				d_fee = CommonHelper.strip_float(t[2])
		return {'total_price': total,
				'delivery_fee': d_fee,
				'tip': tip}

class ToastHelper(CommonHelper):
	
	@staticmethod
	def partner(val):
		return re.split(r':|<', val, maxsplit=2)[1].strip()


	@staticmethod
	def customer(val):
		f = dict()
		partner, deliver_by, customer_name, address, customer_phone = str(), str(), str(), str(), str()
		delivery_fee, tip, total_price = float(), float(), float()
		for i in val:
			t = i.text.splitlines()
			#print(t)
			if t[1] == 'Deliver by':
				#truly the strangest error ive even encountered
				#in shell, or in a differnt module '5:02 pm EDT' is strped with '%I:%M %p %Z'
				#but here in this function, it does not(no match error)...
				#try it again, or post it on reddit
				deliver_by = t[2].replace('EDT', '').strip()
				try:
					t=datetime.strptime(deliver_by, "%I:%M %p")
					d=dt.date(2020, 5, 12)
					deliver_by = eastern.localize(datetime.combine(d, t.time())).astimezone(pytz.utc)
				except Exception as e:
					print(e)
			elif t[1] == 'Customer Info':
				t = list(filter(lambda t: t!='', t))
				customer_name = t[1].strip()
				address = t[2].strip()
				print(t[2])
				customer_phone = t[3].strip()
				#print(t)
				#f['address'] = ''.join(t[2:])
			elif t[1] == 'Delivery Fee':
				delivery_fee = CommonHelper.strip_float(t[2])
			elif t[1] == 'Tip':
				tip == CommonHelper.strip_float(t[2])
			elif t[1] == 'Total':
				total_price = CommonHelper.strip_float(t[2])
		return {'deliver_by': deliver_by, 'customer_name': customer_name,
				'address': address, 'customer_phone': customer_phone,
				'delivery_fee': delivery_fee, 'tip': tip, 'total_price': total_price}

	@staticmethod
	def order(val):
		return CommonHelper.strip_order(val.text)
