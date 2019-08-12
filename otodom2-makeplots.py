#!/usr/bin/python3
import mysql.connector as mariadb
import matplotlib.pyplot as plt
import numpy
from textwrap import wrap
import os


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
	return medians,av_prices,av_sizes,av_rooms,quantities,filter_names



#generates png file with plot
def save_plot(x_list,y_list,xlabel,filename,title):
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
	
#generates html file, that display png image inside
def save_html(title,filename):
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
	
	
	</head>
	
	<body>
	<script src="cookies.js"></script>
	<h1>"""+title+"""</h1>
	</br></br></br>
	<IMG SRC="""+filename+""".png>
	
	
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
	<body><h1>Na stronie prezentuję statystyki dotyczące rynku mieszkaniowego w Polsce.</h1>
	</br>Dane zbieram hobbystycznie, samodzielnie analizując ogłoszenia sprzedaży.</br></br>
	
	
	"""
	
	for title,filename in zip(titles,filenames):
		output+='<a href="./'+filename+'.html" target="right">'+title+'</a><br><br>'
	
	output+="</html>"
	
	with open ("html/left.html","w") as file:
		file.write(output)
	

date=', sierpień 2019'	
titles=['Mediana cen mieszkań - rynek pierwotny (0-250metrów)',
		'Średnie rozmiary mieszkań - rynek pierwotny (0-250metrów)',
		'Średnia ilość pokoi - rynek pierwotny (0-250metrów)',
		'Ilość ofert - rynek pierwotny (0-250metrów)',
		'Mediana cen mieszkań - rynek wtórny (0-250metrów)',
		'Średnie rozmiary mieszkań - rynek wtórny (0-250metrów)',
		'Średnia ilość pokoi - rynek wtórny (0-250metrów)',
		'Ilość ofert - rynek wtórny (0-250metrów)'
		]	
filenames=[ 'pierwotny_mediana',
			'pierwotny_rozmiar',
			'pierwotny_ilosc_pokoi',
			'pierwotny_ilosc_ofert',
			'wtorny_mediana',
			'wtorny_rozmiar',
			'wtorny_ilosc_pokoi',
			'wtorny_ilosc_ofert'
			]
			
medians,av_prices,av_sizes,av_rooms,quantities,filter_names=get_av_data("%pierwotny","2019-08-01")

title,filename=titles[0],filenames[0]
save_plot(medians,filter_names,'Cena',filename,title+date)
save_html(title,filename)

title,filename=titles[1],filenames[1]
save_plot(av_sizes,filter_names,'Rozmiar',filename,title+date)
save_html(title,filename)

title,filename=titles[2],filenames[2]
save_plot(av_rooms,filter_names,'Ilość pokoi',filename,title+date)
save_html(title,filename)

title,filename=titles[3],filenames[3]
save_plot(quantities,filter_names,'Ilość ofert',filename,title+date)
save_html(title,filename)



medians,av_prices,av_sizes,av_rooms,quantities, filter_names=get_av_data("%wtórny","2019-08-01")

title,filename=titles[4],filenames[4]
save_plot(medians,filter_names,'Cena',filename,title+date)
save_html(title,filename)

title,filename=titles[5],filenames[5]
save_plot(av_sizes,filter_names,'Rozmiar',filename,title+date)
save_html(title,filename)

title,filename=titles[6],filenames[6]
save_plot(av_rooms,filter_names,'Ilość pokoi',filename,title+date)
save_html(title,filename)

title,filename=titles[7],filenames[7]
save_plot(quantities,filter_names,'Ilość ofert',filename,title+date)
save_html(title,filename)


save_menu_html(titles,filenames)