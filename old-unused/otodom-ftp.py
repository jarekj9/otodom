import ftplib
session = ftplib.FTP('y4r3k.boo.pl','y4r3k','ph@lenopsis.6578')
file = open('otodom-zabawa.txt','rb')                  # file to send
session.storbinary('STOR httpdocs/otodom-zabawa.txt', file)     # send the file
file.close()                                    # close file and FTP
session.quit()
