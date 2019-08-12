#It prints summary of prices from files, adds '#' to represent change in peak of price
def hashgen(startvalue,filename):
    av_price, dates, count=[],[],[]
    with open(filename) as file:                #get dates, offer counts and average prices
        for line in file:
            if "Average" in line:
                av_price.append(line.split("Average: ")[1].strip())
            if "Date" in line:
                dates.append(line.split(" ")[1].strip())
            if "offers" in line:
                count.append(line.split(" ")[3].strip())

    file.close()

    av_price_mod=[]                             #this will represent just peak of price with '###'
    for price in av_price:
        av_price_mod.append((int(price)-startvalue)//500)


    hashes=""
    print(str(startvalue)+" +")
    print("|")
    print("\/")
    for index, number in enumerate(av_price_mod):
        for x in range(number):
            hashes+="#"
        print(dates[index]+" "+hashes+" "+av_price[index]+" ("+count[index]+" offers)")
        hashes=""

print("Mieszkania po roku 2000, rynek wtorny, blok, 3 pokoje, 50-60m:\n")
hashgen(325000,"otodom-50-60-po2000.txt")
print("\nMieszkania po roku 2000, rynek wtorny, blok, 2-3 pokoje, 42-52m:\n")
hashgen(275000,"otodom-42-52-po2000.txt")
print("\nMieszkania przed rokiem 2000, 3 pokoje, 50-60m:\n")
hashgen(225000,"otodom-do2000.txt")
print("\nMieszkania przed rokiem 1990, 2 pokoje 33-38m:")
hashgen(150000,"otodom-moje.txt")
print("\nMieszkania rynku pierwotnego, 50-60m")
hashgen(275000,"otodom-pierwotny.txt")

