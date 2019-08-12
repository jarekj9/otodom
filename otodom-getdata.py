from bs4 import BeautifulSoup
import re
import datetime
import requests
import statistics
import mysql.connector as mariadb
import math

def read_prices(name,url):

	result="Date: "+ str(datetime.datetime.now())+"\r\n"
	###url is a link to search results from otodom (can apply any filter)
	###get number of pages:
	r  = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data, "html.parser")
	try:
		offers_nr = soup.find("div", {"class": "offers-index pull-left text-nowrap"}).find("strong").text.encode("utf-8").decode().strip().replace(' ','')
		page_nr = str(math.ceil(int(offers_nr)/24))
	except:
		page_nr="1"

	
	###go through pages:
	all_prices=[]
	for page in range(1, int(page_nr)+1):
		
		result+="Processing page: "+str(page)+" out of "+page_nr+"\r\n"
		url = url+"&page="+str(page)
		
		r  = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data, "html.parser")
		
		rightdiv = soup.find("div", {"class": "col-md-content"})						
		
		###search prices in div
		for i, o in enumerate(rightdiv):
			if "promo_top_ads" in str(o) : continue
			try: price = str(o).split('"offer-item-price">')[1].split('</li>')[0].strip()
			except: price=""
			price=re.sub(',..', '', price)							  #remove ',' if it exists
			price2 = re.findall('\d+', price) 
			all_prices.append(''.join(price2))
		
		all_prices = list(filter(None,all_prices))
		all_prices = [int(price) for price in all_prices]

	###print/write results
	result+= "All prices of "+str(len(all_prices))+" offers: "+str(all_prices)+"\r\n"
	sum=0
	for x in all_prices:
		sum+=int(x)
	average = sum // len(all_prices)
	median = int(statistics.median(all_prices))
	result+="Average: "+str(average)+"\r\nMedian: "+str(median)+"\r\n"
	result+="\r\n\r\n"
	
	print (result)
		
	load_to_base(name,all_prices,average,median)



#loads data from 'lista' to database
def load_to_base(filter_name,lista,average,median):


  with open ("mysql.txt","r") as file:
    mysqlpassword = file.readline().strip()

  mariadb_connection = mariadb.connect(user='pi', password=mysqlpassword, database='DB')
  cursor = mariadb_connection.cursor()
  #insert all information to first table
  for price in lista:
    try:
      cursor.execute("INSERT INTO otodom_alldata (date,price,filter_name) VALUES (CURRENT_DATE,%s,%s)", (price,filter_name))
    except mariadb.Error as error:
      print("Error: {}".format(error))
   
  #insert average prices to second table
  try:
    cursor.execute("INSERT INTO otodom_average (date,av_price,filter_name,median) VALUES (CURRENT_DATE,%s,%s,%s)", (average,filter_name,median))
  except mariadb.Error as error:
    print("Error: {}".format(error))

  #insert quantity for each filter
  try:
    cursor.execute("INSERT INTO otodom_quantity (date,quantity,filter_name) VALUES (CURRENT_DATE,%s,%s)", (len(lista),filter_name))
  except mariadb.Error as error:
    print("Error: {}".format(error))

  mariadb_connection.commit()
  print ("The last inserted id was: ", cursor.lastrowid)

  mariadb_connection.close()



	
#po roku 2000, 3 pokoje, 50-60m, rynek wtorny	
read_prices("otodom-50-60-po2000","https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/?search%5Bfilter_float_m%3Afrom%5D=50&search%5Bfilter_float_m%3Ato%5D=60&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_float_build_year%3Afrom%5D=2000&search%5Bdescription%5D=1&search%5Bdist%5D=0&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184")

#po roku 2000, 2-3 pokoje, 42-52, rynek wtorny
read_prices("otodom-42-52-po2000", "https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/?search%5Bfilter_float_m%3Afrom%5D=42&search%5Bfilter_float_m%3Ato%5D=52&search%5Bfilter_enum_rooms_num%5D%5B0%5D=2&search%5Bfilter_enum_rooms_num%5D%5B1%5D=3&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_float_build_year%3Afrom%5D=2000&search%5Bdescription%5D=1&search%5Bdist%5D=0&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184")

#przed rokiem 2000, blok, 3 pokoje, 50-60m, rynek wtorny
read_prices("otodom-do2000","https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/blok/?search%5Bfilter_float_m%3Afrom%5D=50&search%5Bfilter_float_m%3Ato%5D=60&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_float_build_year%3Ato%5D=2000&search%5Bdescription%5D=1&search%5Bdist%5D=0&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184")

#przed rokiem 1990, 2 pokoje, 33-38m, rynek wtorny
read_prices("otodom-moje","https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/blok/?search%5Bfilter_float_m%3Afrom%5D=33&search%5Bfilter_float_m%3Ato%5D=38&search%5Bfilter_enum_rooms_num%5D%5B0%5D=2&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_float_build_year%3Ato%5D=1990&search%5Bdescription%5D=1&search%5Bdist%5D=0&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184")

#rynek pierwotny, 3 pokoje, 50-60m
read_prices("otodom-pierwotny","https://www.otodom.pl/sprzedaz/nowe-mieszkanie/bydgoszcz/apartamentowiec--blok/?search%5Bfilter_float_m%3Afrom%5D=50&search%5Bfilter_float_m%3Ato%5D=60&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_market%5D%5B0%5D=primary&search%5Bdescription%5D=1&search%5Bdist%5D=0&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184")

