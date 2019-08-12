#!/usr/bin/python3
import ftplib
import os

#returns list of filenames, that contain some name, from current folder
def give_filenames(name):
    filenames=[]
    all_files=os.listdir('html/')    #in python2 need to give dir: os.listdir('/home')
    
    for file in all_files:
        if name in file:
            filenames.append(file)
    return filenames

	
with open ("ftp.txt","r") as file:
		lines = file.readlines()
		ftpserver = lines[0].strip()
		ftpuser = lines[1].strip()
		ftppass = lines[2].strip()

session = ftplib.FTP(ftpserver,ftpuser,ftppass)
files=give_filenames(".")	
	
for file in files:
	f = open('html/'+file,'rb')                
	session.storbinary('STOR ceny-mieszkan.online/'+file, f)     # send the file
	f.close()  

session.quit()
