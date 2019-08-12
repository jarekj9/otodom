#!/usr/bin/python3
from bs4 import BeautifulSoup
import re
import datetime
import requests
import statistics
import mysql.connector as mariadb
import math

#to use via TOR
def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:8089',
                       'https': 'socks5://127.0.0.1:8089'}
    return session




#returns list of dicts with otodom data
#url is a link to search results from otodom (can apply any filter)
#filter_name is just a name it will use when loading results to database
def read_prices(filter_name,url):
	
	result="Date: "+ str(datetime.datetime.now())+"\r\n"
	
	###get number of pages:
	#r = requests.get(url)   #standard connection, no TOR
	
	
	r = get_tor_session().get(url) # Make a request through the Tor connection

	data = r.text
	soup = BeautifulSoup(data, "html.parser")
	try:
		offers_nr = soup.find("div", {"class": "offers-index pull-left text-nowrap"}).find("strong").text.encode("utf-8").decode().strip().replace(' ','')
		page_nr = str(math.ceil(int(offers_nr)/72))
	except:
		page_nr="1"

	
	###go through pages:
	all_data=[]
	for page in range(1, int(page_nr)+1):
		
		print("Processing page: "+str(page)+" out of "+page_nr)
		url = url+"&page="+str(page)
		
		try:
			#r	= requests.get(url)
			r = get_tor_session().get(url)
			data = r.text
			soup = BeautifulSoup(data, "html.parser")
			rightdiv = soup.find("div", {"class": "col-md-content"})	
		except: continue
		
		###search prices in div
		for i, obj in enumerate(rightdiv):
			if "promo_top_ads" in str(obj) : continue
			try: price = str(obj).split('"offer-item-price">')[1].split('</li>')[0].strip()
			except: continue
			
			price=re.sub(',..', '', price)								#remove ',' if it exists and get just digits
			price = ''.join(re.findall('\d+', price))
			if price == "": continue
			
			room = str(obj).split('"offer-item-rooms hidden-xs">')[1].split('</li>')[0]
			room = re.findall('\d', room)[0]
			
			size = str(obj).split('"hidden-xs offer-item-area">')[1].split('</li>')[0]
			size = re.findall(r"[0-9]*,?[0-9]+", size)[0]
			size = float(size.replace(',','.'))
			
			seller = obj.find("li", {"class": "pull-right"}).text.strip()
			
			title = obj.find("span", {"class": "offer-item-title"}).text.strip()
			
			try: location = str(obj).split('Mieszkanie na sprzedaż: </span>')[1].split('</p>')[0]
			except: location = "" 
						
			all_data.append({'price':price,
							 'room':room,
							 'size':size,
							 'location':location,
							 'seller':seller,
							 'title':title})


	###print/write results
	result += "All data: "+str(all_data)+"\n"
	sum=0
	for entry in all_data:
		sum += int(entry.get('price'))
	prices = [int(entry.get('price')) for entry in all_data]
	average = sum // len(prices)
	median = int(statistics.median(prices))
	
	sizes = [float(entry.get('size')) for entry in all_data]
	av_size = round(statistics.mean(sizes),2)
	
	room = [float(entry.get('room')) for entry in all_data]
	av_room = round(statistics.mean(room),2)
	
	result += "Average: "+str(average)+"\r\nMedian: "+str(median)+"\r\n"
	result += "Average size: "+str(av_size)+"\r\nAverage Rooms: "+str(av_room)+"\r\n"
	result += "\r\n\r\n"
	
	print (result)
	print("Loading to base...")
	load_to_base(filter_name,all_data,average,median,av_size,av_room)
	print("Done.")



#loads data from 'all_data' to database
def load_to_base(filter_name,all_data,average,median,av_size,av_room):
	
	with open ("mysql.txt","r") as file:
		mysqlpassword = file.readline().strip()
	
	mariadb_connection = mariadb.connect(user='pi', password=mysqlpassword, database='OTODOM_MIASTA')
	cursor = mariadb_connection.cursor()
	#insert all information to first table
	for entry in all_data:

		try:
			cursor.execute("INSERT INTO otodom_alldata (date,price,room,size,location,seller,title,filter_name) VALUES (CURRENT_DATE,%s,%s,%s,%s,%s,%s,%s)",
			(entry.get('price'),entry.get('room'),entry.get('size'),entry.get('location'),entry.get('seller'),entry.get('title'),filter_name))
		except mariadb.Error as error:
			print("Error: {}".format(error))

	#insert average prices to second table
	try:
		cursor.execute("INSERT INTO otodom_average (date,av_price,median,av_size,av_room,quantity,filter_name) VALUES (CURRENT_DATE,%s,%s,%s,%s,%s,%s)",
		(average,median,av_size,av_room,len(all_data),filter_name))
	except mariadb.Error as error:
		print("Error: {}".format(error))

	mariadb_connection.commit()
	print ("The last inserted id was: ", cursor.lastrowid)

	mariadb_connection.close()


print ("Starting scrapping... "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
#read_prices("test","https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/apartamentowiec--blok/?search%5Bfilter_float_m%3Afrom%5D=45&search%5Bfilter_float_m%3Ato%5D=55&search%5Bfilter_enum_rooms_num%5D%5B0%5D=2&search%5Bfilter_enum_rooms_num%5D%5B1%5D=3&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_enum_floor_no%5D%5B0%5D=floor_1&search%5Bfilter_enum_floor_no%5D%5B1%5D=floor_2&search%5Bfilter_float_build_year%3Afrom%5D=2000&search%5Bfilter_enum_extras_types%5D%5B0%5D=balcony&search%5Bdescription%5D=1&search%5Border%5D=created_at_first%3Adesc&search%5Bcity_id%5D=184&nrAdsPerPage=72")

#Wszystkie do 10 pokoi, do 250m
"""
read_prices("Bydgoszcz, rynek pierwotny","https://www.otodom.pl/sprzedaz/nowe-mieszkanie/bydgoszcz/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=2&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184&nrAdsPerPage=72")
read_prices("Bydgoszcz, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/bydgoszcz/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=2&search%5Bsubregion_id%5D=386&search%5Bcity_id%5D=184&nrAdsPerPage=72")

read_prices("Kraków, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/krakow/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=6&search%5Bsubregion_id%5D=410&search%5Bcity_id%5D=38&nrAdsPerPage=72")
read_prices("Kraków, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/krakow/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=6&search%5Bsubregion_id%5D=410&search%5Bcity_id%5D=38&nrAdsPerPage=72")

read_prices("Łódź, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/lodz/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=5&search%5Bsubregion_id%5D=127&search%5Bcity_id%5D=1004&nrAdsPerPage=72")
read_prices("Łódź, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/lodz/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=5&search%5Bsubregion_id%5D=127&search%5Bcity_id%5D=1004&nrAdsPerPage=72")

read_prices("Wrocław, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/wroclaw/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=1&search%5Bsubregion_id%5D=381&search%5Bcity_id%5D=39&nrAdsPerPage=72")
read_prices("Wrocław, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/wroclaw/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=1&search%5Bsubregion_id%5D=381&search%5Bcity_id%5D=39&nrAdsPerPage=72")

read_prices("Poznań, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/poznan/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=15&search%5Bsubregion_id%5D=462&search%5Bcity_id%5D=1&nrAdsPerPage=72")
read_prices("Poznań, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/poznan/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=15&search%5Bsubregion_id%5D=462&search%5Bcity_id%5D=1&nrAdsPerPage=72")

read_prices("Gdańsk, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/gdansk/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=439&search%5Bcity_id%5D=40&nrAdsPerPage=72")
read_prices("Gdańsk, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/gdansk/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=439&search%5Bcity_id%5D=40&nrAdsPerPage=72")

read_prices("Szczecin, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/szczecin/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=16&search%5Bsubregion_id%5D=371&search%5Bcity_id%5D=213&nrAdsPerPage=72")
read_prices("Szczecin, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/szczecin/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=16&search%5Bsubregion_id%5D=371&search%5Bcity_id%5D=213&nrAdsPerPage=72")

read_prices("Lublin, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/lublin/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=3&search%5Bsubregion_id%5D=396&search%5Bcity_id%5D=190&nrAdsPerPage=72")
read_prices("Lublin, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/lublin/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=3&search%5Bsubregion_id%5D=396&search%5Bcity_id%5D=190&nrAdsPerPage=72")
"""
read_prices("Białystok, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/bialystok/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=10&search%5Bsubregion_id%5D=434&search%5Bcity_id%5D=204&nrAdsPerPage=72")
read_prices("Białystok, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/bialystok/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=10&search%5Bsubregion_id%5D=434&search%5Bcity_id%5D=204&nrAdsPerPage=72")

read_prices("Warszawa, rynek pierwotny", "https://www.otodom.pl/sprzedaz/nowe-mieszkanie/warszawa/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bdescription%5D=1&search%5Bregion_id%5D=7&search%5Bsubregion_id%5D=197&search%5Bcity_id%5D=26&nrAdsPerPage=72")
read_prices("Warszawa, rynek wtórny", "https://www.otodom.pl/sprzedaz/mieszkanie/warszawa/?search%5Bfilter_float_m%3Ato%5D=250&search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search%5Bfilter_enum_rooms_num%5D%5B1%5D=2&search%5Bfilter_enum_rooms_num%5D%5B2%5D=3&search%5Bfilter_enum_rooms_num%5D%5B3%5D=4&search%5Bfilter_enum_rooms_num%5D%5B4%5D=5&search%5Bfilter_enum_rooms_num%5D%5B5%5D=6&search%5Bfilter_enum_rooms_num%5D%5B6%5D=7&search%5Bfilter_enum_rooms_num%5D%5B7%5D=8&search%5Bfilter_enum_rooms_num%5D%5B8%5D=9&search%5Bfilter_enum_rooms_num%5D%5B9%5D=10&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bdescription%5D=1&search%5Bregion_id%5D=7&search%5Bsubregion_id%5D=197&search%5Bcity_id%5D=26&nrAdsPerPage=72")


print("Finished... "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

