from datetime import datetime, timedelta
import pytz
#address, customer_name, customer_phone,'partner, order_number
#deliver_by, total price, tip, delivery_fee, note,

#FORMAT

#source = toast, 
#1720a7ec7956d9da
toast1 = {'address': '600 Harrison St301Hoboken, NJ 07030',
	 	  'customer_name': 'Alexandra Bernal', 'customer_phone':'646-322-1508',
	      'partner': 'Shaka Bowl', 'order_number':'74', 'deliver_by': datetime(2020, 5, 12, 21, 2).astimezone(pytz.utc),
	      'total_price': 17.23, 'tip': float(0), 'delivery_fee': 4.99, 'note':''}

#source = gloria
#1720a8189e044a41
gloria1 = {'address':'66 Hudson Pl, 07086, Weehawken', 'customer_name':'Eugene Ryazanov', 'customer_phone':'+17326729877',
		   'partner':'Apulia','order_number':'103046459','deliver_by':datetime.now().astimezone(pytz.utc),
           'total_price': 56.7, 'tip': float(0), 'delivery_fee': 4.5, 
           'note':' "No-contact / Leave order at my door" Client acknowledged'}

#1720a81b070bb42a
gloria2 = {'address':'1112 Park Avenue, #1R, 07030, Hoboken','customer_name':'Christian Pimsner',
		   'customer_phone':'+19178424588', 'partner':'Apulia','order_number':'103033707',
		   'deliver_by':datetime(2020, 5, 10, 22, 30).astimezone(pytz.utc),'total_price': 87.98, 
		   'tip':11.48,
		   'delivery_fee': 4.50, 'note':' "Meet driver outside" Client acknowledged'}

#source = brand
#1720a7fe22681dc9
#deliver_by is now a datetime object
#i need to know if there are ever orders places for specific days tho...
brand1 = {'address':'','customer_name':'Nautica Smith','customer_phone':'201-284-1285',
   		  'partner':'Quality Greens Kitchen','order_number':'7633599','deliver_by':datetime(2020, 7, 30, 18, 52).astimezone(pytz.utc),
          'total_price': 12.10, 'tip': float(0),'delivery_fee': float(0),'note':''}

#1720a7f978469107
brand2 = {'address':'415 Jackson Street  Apt / Suite: 2R  Hoboken, NJ 07030','customer_name':'Robert La Rocca',
   		  'customer_phone':'845-520-8788','partner':'Quality Greens Kitchen','order_number':'7634064',
   		  'deliver_by':datetime(2020, 7, 30, 20, 17).astimezone(pytz.utc),'total_price':31.57,'tip': 6.00,
   		  'delivery_fee': 2.50, 'note':'Please call'}

#source = grubhub
#1720a7f6de6ff778
grubhub1 = {"address": "914 Garden St  3  Hoboken, NJ, 07030", "customer_name": "Sarah M",
			"customer_phone": "(646) 812-3322", "partner": "Alfalfa", "order_number": " #68911154 — 8665633",
			"deliver_by": datetime(2020, 5, 12, 20, 9).astimezone(pytz.utc), 'delivery_fee': 1.99, "total_price": 33.89, "tip": 5.65, "note": ''}

#1720a7f3b2241cad
grubhub2 = {'address': '499 Washington Blvd  14th Floor  Jersey City, NJ, 07310', 'customer_name': "Stephanie G",
			"customer_phone": "(914) 960-5194", "partner": "Quality Greens Kitchen", "order_number": " #47571154 — 3448843",
			"deliver_by": datetime(2020, 5, 12, 20, 29).astimezone(pytz.utc), "total_price": 45.56, "tip": 7.59, "delivery_fee": 4.99,
			"note": ' Call when downstairs and producer will come down to meet delivery person. '}

#source = delivery
#1720a81062ba6754
#idk what to do with asap...maybe 35 mins...and i assume sometimes these things have actual dates/times
delivery1 = {"address": "pickup", "customer_name": "Kaitlin Wieners", "customer_phone": "917-428-4925",
			"partner": "Alfalfa", "order_number": "30245882", "deliver_by": " FUTURE  PICKUP   (Hold)",
			"total_price": 14.56, "tip": 2.3, "delivery_fee": float(0), "note": ''}

#1720a8040e82bbb2
delivery2 = {"address": "505 Monroe St Unit:  2BHoboken,  NJ  07030", "customer_name": "Megan Smith",
			 "customer_phone": "347-880-2709", "partner": "Urban Coalhouse Pizza + Bar", "deliver_by": " Deliver ASAP ",
			 "total_price": 31.19, "tip": 3.60, "delivery_fee": 2.00, 
			 'note': '**Contactless delivery - Please leave order outside my doorstep. Please call upon arrival*Please do not include any kind of cutlery',
			 "order_number": "30247647"}


#source = chow now
#1720a7e13012f4f5
#neither html has a deliver_by
chow1 = {"address":"308 Willow Ave  Main Entrance Hosp  Hoboken, NJ 07030", "customer_name": "Kristin McKitish",
		 "customer_phone": "(908) 787-3675", "partner": "Alfalfa", "deliver_by": "", 'order_number': "67248022",
		 "total_price": 32.70, "tip": 3.79, "delivery_fee": 1.99, 'note': ''}

#1720a7e65e5d61ab
chow2 = {"address": "1450 Washington St  1001  Hoboken, NJ 07030", "customer_name": "Dan Reider", 
		 "customer_phone":"(908) 938-4908", "partner": "Alfalfa", "deliver_by": '', "order_number": "67241209",
		 "total_price": 24.78, "tip": 2.00, "delivery_fee": 1.99, 'note': ''}


toast = [{'email_id': "1720a7ec7956d9da", 'body': toast1}]
gloria = [{'email_id': "1720a8189e044a41", 'body': gloria1}, {'email_id':"1720a81b070bb42a",'body':gloria2}]
brand = [{'email_id': '1720a7fe22681dc9', 'body': brand1}, {'email_id':"1720a7f978469107", 'body':brand2}]
grubhub = [{'email_id': '1720a7f6de6ff778' ,'body':grubhub1}, {'email_id':'1720a7f3b2241cad', 'body': grubhub2}]
delivery = [{"email_id": "1720a81062ba6754", "body": delivery1}, {'email_id': "1720a8040e82bbb2", 'body': delivery2}]
chow = [{'email_id': "1720a7e13012f4f5", "body": chow1}, {"email_id": "1720a7e65e5d61ab", "body":chow2}]
_all = [*toast, *gloria, *brand, *grubhub, *delivery, *chow]

EXPORT = {"toasttab.com": toast, "grubhub.com": grubhub, "gloriafood.com": gloria, "delivery.com": delivery,
		  "chownow.com": chow, "brandibble": brand}

def check_key_length():
	prev = len(list(_all[0].keys()))
	for i in range(1, len(_all)):
		if not prev == len(list(_all[i].keys())):
			print("keys vary")
			return None
	print('keys are equal')


if __name__ == "__main__":
	check_key_length()
	#do not use test dicts if keys vary
