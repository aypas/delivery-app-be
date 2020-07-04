import re

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
			if re.match(r"^\+|^(.*?)|^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", i):
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
		phone_num = str()
		if not b:
			address = 'probs pickup'
			#check to see if order is for pickup
		else:
			address = val[index-1]+val[index]
			if CommonHelper.strip_phone_num([val[index+1]])!=None:
				phone_num = val[index+1]
		if not phone_num:
			phone_num = CommonHelper.strip_phone_num(val)


		return {'customer_phone': phone_num,
				'address': address,
				'customer_name': name}

class GloriaHelper(CommonHelper):

	@staticmethod
	def ordern_and_rname(val):
		t = val.split('-')
		return CommonHelper.strip_order(t[1]), t[0]

	@staticmethod
	def date_time(val):
		#print(val)
		for i in range(len(val)):
			if CommonHelper.match_time(val[i]):
				return i

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
			if p:=CommonHelper.strip_phone_num(val):
				phone = p 
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

		return {'total': total,
				'tip': tip,
				'delivery_fee': delivery_fee}


class BrandHelper(CommonHelper):
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
				print(address, 'hellooooo\n')
			elif t[0] == 'Phone':
				phone_num = t[1].strip()
			elif t[0] == 'Order ID':
				order_id = t[1].strip()
			elif 'Store' == t[0]:
				partner = t[1].strip()
			elif 'Requested Time' == t[0]:
				deliver_by = t[1]
			elif 'Order Type' == t[0]:
				if t[1].strip()=='Pick-Up':
					address = str()
					order_type == 'pick-up'
				else:
					order_type = 'delivery'

		return {'customer_name': name,
				'address': address,
				'customer_phone': phone_num,
				'order_id': order_id,
				'partner': partner,
				'deliver_by': deliver_by}

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
		return {'total': total,
				'delivery_fee': d_fee,
				'tip': tip}

class ToastHelper(CommonHelper):
	@staticmethod
	def prices(val):
		pass

	@staticmethod
	def customer(val):
		f = dict()
		for i in val:
			t = i.text.splitlines()
			#print(t)
			if t[1] == 'Deliver by':
				f['deliver_by'] = t[2]
			elif t[1] == 'Customer Info':
				t = list(filter(lambda t: t!='', t))
				f['customer_name'] = t[1].strip()
				f['address'] = t[2].strip()
				f['customer_phone'] = t[3].strip()
				#print(t)
				#f['address'] = ''.join(t[2:])
			elif t[1] == 'Delivery Fee':
				f['delivery_fee'] = CommonHelper.strip_float(t[2])
			elif t[1] == 'Tip':
				f['tip'] == CommonHelper.strip_float(t[2])
			elif t[1] == 'Total':
				f['total'] = CommonHelper.strip_float(t[2])
			elif t[1] == 'Restaurant Info':
				t = list(filter(lambda t: t!='', t))
				print(t)
				for i in range(len(t[1])):
					if t[1][i].isdigit():
						f['partner'] = t[1][:i].strip()
						break
		return f

	@staticmethod
	def order(val):
		return CommonHelper.strip_order(val.text)
