#!/usr/bin/python3
import mysql.connector as mariadb
import matplotlib.pyplot as plt
import numpy
from textwrap import wrap
import os
import unidecode
# -*- coding: UTF-8 -*-


#retrieving information

def get_av_data(filter_name,date):

	with open ("mysql.txt","r") as file:
		mysqlpassword = file.readline().strip()

	mariadb_connection = mariadb.connect(user='pi', password=mysqlpassword, database='OTODOM_MIASTA')
	cursor = mariadb_connection.cursor()
	cursor.execute("SELECT median, av_price, av_size, av_room, quantity, filter_name FROM otodom_average WHERE filter_name LIKE '"+filter_name+"' AND DATE='"+date+"'")
	medians,av_prices,av_sizes,av_rooms,quantities,filter_names=[],[],[],[],[],[]
	for median,av_price,av_size,av_room,quantity,filter_name in cursor:
		medians.append(median)
		av_prices.append(int(av_price))
		av_sizes.append(av_size)
		av_rooms.append(av_room)
		quantities.append(quantity)
		filter_names.append(filter_name)

	mariadb_connection.close()
	
	data = {'medians':medians,
			'av_prices':av_prices,
			'av_sizes':av_sizes,
			'av_rooms':av_rooms,
			'quantities':quantities,
			'filter_names':filter_names}	
	return data



#generates png file with plot
def save_plot(x_list,y_list,xlabel,filename,title):
	plt.switch_backend('agg')    #necessary if script run from linux
	plt.rcParams.update({'font.size': 6})
	plt.rcParams.update({'figure.autolayout': True})

	fig, ax = plt.subplots()
	fig.set_dpi(150)
	y_pos = numpy.arange(len(y_list))

	ax.barh(y_pos, x_list, align='center')
	ax.set_yticks(y_pos)
	ax.set_yticklabels(y_list)
	ax.invert_yaxis()  # labels read top-to-bottom
	ax.set_xlabel(xlabel)
	ax.set_title(title)

	plt.savefig("html/"+filename+'.png')
	
	plt.close('all')
	
#generates html file, that display png image inside
def save_html(title,filename,pretext,posttext):
	lines="""<!DOCTYPE html>
	<html lang="pl-PL">
	<head>
	<title>"""+title+"""</title>
	<meta name="Ceny mieszkań" content="Ceny mieszkań">
	<meta name="keywords" content="Ceny mieszkań,ceny mieszkan, rynek nieruchomości, statystyki mieszkan, ceny nieruchomości, rynek mieszkaniowy">

	<meta charset="UTF-8">
	<link rel="stylesheet" href="style.css" />

	<!-- Global site tag (gtag.js) - Google Analytics -->
	<script async src="https://www.googletagmanager.com/gtag/js?id=UA-145155413-1"></script>
	<script>
	  window.dataLayer = window.dataLayer || [];
	  function gtag(){dataLayer.push(arguments);}
	  gtag('js', new Date());

	  gtag('config', 'UA-145155413-1');
	</script>
	
	<!-- Adsense -->
	<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
	<script>
     (adsbygoogle = window.adsbygoogle || []).push({
          google_ad_client: "ca-pub-9290215832490467",
          enable_page_level_ads: true
     });
	</script>
	<script async custom-element="amp-auto-ads"
        src="https://cdn.ampproject.org/v0/amp-auto-ads-0.1.js">
	</script>

	
	</head>
	
	<body>
	<!-- Adsense -->
	<amp-auto-ads type="adsense"
              data-ad-client="ca-pub-9290215832490467">
	</amp-auto-ads>
	
	
	<script src="cookies.js"></script>
	<h1>"""+title+"""</h1>
	</br></br></br>
	"""+pretext+"""
	<IMG SRC="""+filename+""".png>
	</br></br>Poszczególne wartości dla każdego miasta z wykresu:</br>
	"""+posttext+"""
	
	
	</body></html>"""
	
	
	with open ("html/"+filename+'.html','w') as file:
		file.write(lines)

#generates html menu file with links to other pages( that have png plots)
def save_menu_html(titles,filenames):
	
	output="""
	<!DOCTYPE html>
	<html lang="pl-PL">
	<head>
	<title>Ceny mieszkań</title>
	<meta name="Ceny mieszkań" content="Ceny mieszkań">
	<meta name="keywords" content="Ceny mieszkań,ceny mieszkan, rynek nieruchomości, statystyki mieszkan, ceny nieruchomości, rynek mieszkaniowy">

	<meta charset="UTF-8">
	
	<!-- Global site tag (gtag.js) - Google Analytics -->
	<script async src="https://www.googletagmanager.com/gtag/js?id=UA-145155413-1"></script>
	<script>
	  window.dataLayer = window.dataLayer || [];
	  function gtag(){dataLayer.push(arguments);}
	  gtag('js', new Date());

	  gtag('config', 'UA-145155413-1');
	</script>
	
	<!-- Adsense -->
	<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
	<script>
     (adsbygoogle = window.adsbygoogle || []).push({
          google_ad_client: "ca-pub-9290215832490467",
          enable_page_level_ads: true
     });
	</script>
	
	<meta charset="UTF-8">
	</head>
	<body><h2>Na stronie prezentuję statystyki dotyczące rynku mieszkaniowego w Polsce.
	</h2>
	</br>Dane zbieram hobbystycznie, samodzielnie analizując ogłoszenia sprzedaży ogólnodostępne w mediach. 
	Wykresy mają charakter orientacyjny, ponieważ nie mogę być pewny, 
	że nie wkrednie się w nie jakiś błąd, jednak sądzę, że dobrze oddają sytuację na rynku.
	Dla różnych metrarzy dostępne są wykresy przedstawiające medianę cen, średni rozmiar, średnią ilość pokoi, ilość ofert.</br></br>
	
	
	"""
	
	for title,filename in zip(titles,filenames):
		output+='<a href="./'+filename+'.html" target="right">'+title+'</a><br><br>'
	
	output+="</html>"
	
	with open ("html/left.html","w") as file:
		file.write(output)

def name_to_filename(name):
	# -*- coding: UTF-8 -*-
	filename = unidecode.unidecode(name).replace(" ","").replace("-","_").replace("(","").replace(")","").lower()
	return filename	
	
#generates some additional text for html pages
def generate_description(chart,alldata):
	pretext,posttext="",""
	
	#Sentence with average value
	if chart.get('feature') == 'medians':	pretext += 'Dla przeanalizowanych ogłoszeń średnia z median cen mieszkań dla wszystkich miast wynosi '
	if chart.get('feature') == 'av_sizes':	pretext += 'Pośród wszystkch ofert w tym filtrze średni rozmiar mieszkania to '
	if chart.get('feature') == 'av_rooms':	pretext += 'Uśredniona liczba pokoi występująca w ogłoszeniach tego typu daje liczbę: '
	if chart.get('feature') == 'quantities':pretext += 'Łączna zaleziona w mediach ilość ofert na tego typu mieszkania to '

	number = sum(alldata.get(chart.get('feature')))/len(alldata.get(chart.get('feature')))  #count average of specific feature, like price or number of offers
	pretext += str(round(number,1))+"</br>"
	
	#2 sentences about min and max value
	minval   = min(alldata.get(chart.get('feature')))
	minindex = alldata.get(chart.get('feature')).index(minval)
	maxval = max(alldata.get(chart.get('feature')))
	maxindex = alldata.get(chart.get('feature')).index(maxval)
	pretext += "Dla tego wykresu najniższa z wartości występuje dla miasta "+alldata.get('filter_names')[minindex].split(',')[0]+" i wynosi "+str(minval)+".</br>"
	pretext += "Z kolei najwyższą wartość prezentują dane dla miasta "+alldata.get('filter_names')[maxindex].split(',')[0]+" i jest to "+str(maxval)+".</br>"
	
	#Values under the chart
	for city,value in zip(alldata.get('filter_names'),alldata.get(chart.get('feature'))):
		posttext+="Miasto: "+city.split(',')[0]+", Wartość: "+str(value)+"</br>"
	
	return pretext,posttext
	
#to add new chart, define new lines below
#title is used as chart title and to generate filename, xlabel is for x axis description, sqlfilter is filter for sql query, feature is data (prices,sizes etc)
date=', wrzesień 2019'	
charts=[{'title': 'Mediana cen mieszkań - rynek pierwotny (0-250 metrów)', 	   'xlabel':'Cena', 	  'sqlfilter':("%pierwotny",	 "2019-09-08"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek pierwotny (0-250 metrów)','xlabel':'Rozmiar', 	  'sqlfilter':("%pierwotny",	 "2019-09-08"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek pierwotny (0-250 metrów)', 	   'xlabel':'Ilość pokoi','sqlfilter':("%pierwotny",	 "2019-09-08"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek pierwotny (0-250metrów)', 			   'xlabel':'Ilość ofert','sqlfilter':("%pierwotny",	 "2019-09-08"),'feature':'quantities'},
		
		{'title': 'Mediana cen mieszkań - rynek wtórny (0-250 metrów)',	 	   'xlabel':'Cena' ,	  'sqlfilter':("%wtórny",		 "2019-09-08"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (0-250 metrów)',   'xlabel':'Rozmiar', 	  'sqlfilter':("%wtórny",		 "2019-09-08"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (0-250 metrów)', 	 	   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny",		 "2019-09-08"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (0-250 metrów)', 				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny",		 "2019-09-08"),'feature':'quantities'},
		
		{'title': 'Mediana cen mieszkań - rynek wtórny (30-40 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 30-40m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (30-40 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 30-40m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (30-40 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 30-40m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (30-40 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 30-40m","2019-09-07"),'feature':'quantities'},
		
		{'title': 'Mediana cen mieszkań - rynek wtórny (45-55 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 45-55m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (45-55 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 45-55m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (45-55 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 45-55m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (45-55 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 45-55m","2019-09-07"),'feature':'quantities'},
		
		{'title': 'Mediana cen mieszkań - rynek wtórny (55-65 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 55-65m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (55-65 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 55-65m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (55-65 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 55-65m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (55-65 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 55-65m","2019-09-07"),'feature':'quantities'},
		
		{'title': 'Mediana cen mieszkań - rynek wtórny (65-75 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 65-75m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (65-75 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 65-75m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (65-75 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 65-75m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (65-75 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 65-75m","2019-09-07"),'feature':'quantities'},
		                                                                                                                                    
		{'title': 'Mediana cen mieszkań - rynek wtórny (75-85 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 75-85m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (75-85 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 75-85m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (75-85 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 75-85m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (75-85 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 75-85m","2019-09-07"),'feature':'quantities'},
		                                                                                                                                  
		{'title': 'Mediana cen mieszkań - rynek wtórny (85-95 metrów)',		   'xlabel':'Cena', 	  'sqlfilter':("%wtórny, 85-95m","2019-09-07"),'feature':'medians'},
		{'title': 'Średnie rozmiary mieszkań - rynek wtórny (85-95 metrów)',   'xlabel':'Rozmiar',	  'sqlfilter':("%wtórny, 85-95m","2019-09-07"),'feature':'av_sizes'},
		{'title': 'Średnia ilość pokoi - rynek wtórny (85-95 metrów)',		   'xlabel':'Ilość pokoi','sqlfilter':("%wtórny, 85-95m","2019-09-07"),'feature':'av_rooms'},
		{'title': 'Ilość ofert - rynek wtórny (85-95 metrów)',				   'xlabel':'Ilość ofert','sqlfilter':("%wtórny, 85-95m","2019-09-07"),'feature':'quantities'},
		]	

for index,chart in enumerate(charts):

	print('Creating chart number '+str(index+1))
	alldata=get_av_data(chart.get('sqlfilter')[0],chart.get('sqlfilter')[1])
	chartdata= alldata.get(chart.get('feature'))
	
	title,filename = chart.get('title'),name_to_filename(chart.get('title'))
	save_plot(chartdata,alldata.get('filter_names'),chart.get('xlabel'),filename,title+date)
	pretext,posttext = generate_description(chart,alldata)
	save_html(title,filename,pretext,posttext)

titles = [chart.get('title') for chart in charts]
filenames = [name_to_filename(title) for title in titles]
save_menu_html(titles,filenames)