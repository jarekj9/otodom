#!/usr/bin/python3
from bs4 import BeautifulSoup
import re
import datetime
import requests
import statistics
import mysql.connector as mariadb
import math



with open ("mysql.txt","r") as file:
	mysqlpassword = file.readline().strip()
filter_name="lalalalala"
mariadb_connection = mariadb.connect(user='pi', password=mysqlpassword, database='OTODOM_MIASTA')
cursor = mariadb_connection.cursor()

cursor.execute("SELECT filter_name FROM filter_names WHERE filter_name='"+filter_name+"'")
row = cursor.fetchone()
if not row: cursor.execute("INSERT INTO filter_names (filter_name) VALUES ('%s')" % (filter_name))

mariadb_connection.close()