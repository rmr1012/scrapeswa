import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(options=options)
from colors import *
import re
from datetime import datetime,timedelta
timeRE=re.compile(r'\d{1,2}:\d{1,2}[A|P]M',re.M)

conditions=[]

from models import *
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session=Session()

from scrapeswa import *

def fetchMyWeekend(weekof):
    friday=getFriday(weekof)
    saturday=friday+timedelta(days=1)
    sunday=saturday+timedelta(days=1)
    monday=sunday+timedelta(days=1)
    print("Checking flights for the weekend of ")
    print(datetime.strftime(friday,"%a %b %d %Y" ))


    FridayOut,SundayBack=getRoundTrip('SJC','LAX',friday,sunday)
    SaturdayOut,MondayBack=getRoundTrip('SJC','LAX',saturday,monday)

    FridayOut2,SundayBack2=getRoundTrip('SFO','LAX',friday,sunday)
    SaturdayOut2,MondayBack2=getRoundTrip('SFO','LAX',saturday,monday)


    allOut=FridayOut+SaturdayOut+FridayOut2+SaturdayOut2
    allBack=SundayBack+MondayBack+SundayBack2+MondayBack2

    goodOut=[]
    goodBack=[]
    for flight in allOut:
        if flight["Leave"]>=friday.replace(hour=19,minute=29) and flight["Arrive"]<saturday.replace(hour=11,minute=30):
            goodOut.append(flight)
    for flight in allBack:
        if flight["Leave"]>=sunday.replace(hour=19,minute=00) and flight["Arrive"]<monday.replace(hour=9,minute=45):
            goodBack.append(flight)
    sortedOut = sorted(goodOut,key=lambda x:x[x['bestAval']]['fare'])
    sortedBack = sorted(goodBack,key=lambda x:x[x['bestAval']]['fare'])
    #print(sortedOut)
    #print(sortedBack)
    if(sortedOut is not None and sortedBack is not None):
        print(color("Your Best Bet for the Weekend of "+datetime.strftime(friday,"%a %b %d %Y" )+" is...",'green'))
        print(color("Flight:"+str(sortedOut[0]["Flight"])+" Leaving "+sortedOut[0]['src']+" "+datetime.strftime(sortedOut[0]['Leave'],"%a '%I:%M %p" ),'blue'))
        print(color("Fare: $"+str(sortedOut[0][sortedOut[0]['bestAval']]['fare'])+"(or "+str(sortedOut[0][sortedOut[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedOut[0][sortedOut[0]['bestAval']]['earn'])+' pts ','yellow'))
        print(color("Flight:"+str(sortedBack[0]["Flight"])+" Arriving "+sortedBack[0]['dst']+" "+datetime.strftime(sortedBack[0]['Arrive'],"%a '%I:%M %p" ),'blue'))
        print(color("Fare: $"+str(sortedBack[0][sortedBack[0]['bestAval']]['fare'])+"(or "+str(sortedBack[0][sortedBack[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedBack[0][sortedBack[0]['bestAval']]['earn'])+' pts ','yellow'))
        print(color("Total: $"+str(sortedOut[0][sortedOut[0]['bestAval']]['fare'] + sortedBack[0][sortedBack[0]['bestAval']]['fare'])+"(or "+str(sortedOut[0][sortedOut[0]['bestAval']]['pts'] + sortedBack[0][sortedBack[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedOut[0][sortedOut[0]['bestAval']]['earn']+sortedBack[0][sortedBack[0]['bestAval']]['earn'])+' pts ','orange'))
        return sortedOut,sortedBack


def fetchHerWeekend(weekof):
    friday=getFriday(weekof)

    saturday=friday+timedelta(days=1)
    sunday=saturday+timedelta(days=1)
    monday=sunday+timedelta(days=1)
    print("Checking flights for the weekend of ")
    print(datetime.strftime(friday,"%a %b %d %Y" ))


    FridayOut,SundayBack=getRoundTrip('LAX','SJC',friday,sunday)
    SaturdayOut,MondayBack=getRoundTrip('LAX','SJC',saturday,monday)

    FridayOut2,SundayBack2=getRoundTrip('LAX','SFO',friday,sunday)
    SaturdayOut2,MondayBack2=getRoundTrip('LAX','SFO',saturday,monday)

    FridayOut3,SundayBack3=getRoundTrip('LGB','OAK',friday,sunday)
    SaturdayOut3,MondayBack3=getRoundTrip('LGB','OAK',saturday,monday)


    allOut=FridayOut+SaturdayOut+FridayOut2+SaturdayOut2+FridayOut3+SaturdayOut3
    allBack=SundayBack+MondayBack+SundayBack2+MondayBack2+SundayBack3+MondayBack3

    goodOut=[]
    goodBack=[]
    for flight in allOut:
        if flight["Leave"]>=friday.replace(hour=19,minute=29) and flight["Arrive"]<saturday.replace(hour=11,minute=30):
            goodOut.append(flight)
    for flight in allBack:
        if flight["Leave"]>=sunday.replace(hour=19,minute=00) and flight["Arrive"]<monday.replace(hour=9,minute=45):
            goodBack.append(flight)
    sortedOut = sorted(goodOut,key=lambda x:x[x['bestAval']]['fare'])
    sortedBack = sorted(goodBack,key=lambda x:x[x['bestAval']]['fare'])
    #print(sortedOut)
    #print(sortedBack)
    if(sortedOut is not None and sortedBack is not None):
        print(color("Her Best Bet for the Weekend of "+datetime.strftime(friday,"%a %b %d %Y" )+" is...",'green'))
        print(color("Flight:"+str(sortedOut[0]["Flight"])+" Leaving "+sortedOut[0]['src']+" "+datetime.strftime(sortedOut[0]['Leave'],"%a '%I:%M %p" ),'blue'))
        print(color("Fare: $"+str(sortedOut[0][sortedOut[0]['bestAval']]['fare'])+"(or "+str(sortedOut[0][sortedOut[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedOut[0][sortedOut[0]['bestAval']]['earn'])+' pts ','yellow'))
        print(color("Flight:"+str(sortedBack[0]["Flight"])+" Arriving "+sortedBack[0]['dst']+" "+datetime.strftime(sortedBack[0]['Arrive'],"%a '%I:%M %p" ),'blue'))
        print(color("Fare: $"+str(sortedBack[0][sortedBack[0]['bestAval']]['fare'])+"(or "+str(sortedBack[0][sortedBack[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedBack[0][sortedBack[0]['bestAval']]['earn'])+' pts ','yellow'))
        print(color("Total: $"+str(sortedOut[0][sortedOut[0]['bestAval']]['fare'] + sortedBack[0][sortedBack[0]['bestAval']]['fare'])+"(or "+str(sortedOut[0][sortedOut[0]['bestAval']]['pts'] + sortedBack[0][sortedBack[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedOut[0][sortedOut[0]['bestAval']]['earn']+sortedBack[0][sortedBack[0]['bestAval']]['earn'])+' pts ','orange'))

        return sortedOut,sortedBack

# [{'a': {'b':9,'c':8}}, {'a': {'b':3,'c':4}}, {'a': {'b':4,'c':5}}]


def fetchWeekend(date):
    mySortedOut,mySortedBack=fetchMyWeekend(date)
    herSortedOut,herSortedBack=fetchHerWeekend(date)

    # fill in db query
    # dbFlight = Flight(flight=flight["Flight"],src=flight["src"],dst=flight["dst"],
    # leave=flight["Leave"],arrive=flight["Arrive"],econAval=True if flight["bestAval"]=="Economy"else False,
    # anytime_fare=flight["Anytime"]['fare'],anytime_earn=flight["Anytime"]['earn'],anytime_pts=flight["Anytime"]['pts'],
    # anytime_epd=flight["Anytime"]['epd'],anytime_ppd=flight["Anytime"]['ppd'],
    # economy_fare=flight["Economy"]['fare'],economy_earn=flight["Economy"]['earn'],economy_pts=flight["Economy"]['pts'],
    # economy_epd=flight["Economy"]['epd'],economy_ppd=flight["Economy"]['ppd'])
    #
    # session.add(dbFlight)
    # session.flush()
    # flight['obj']=dbFlight
    #
    # dbWeekend=Weekend(friday=getFriday(date),my_outbound_id=mySortedOut[0]['obj'].id,my_return_id=mySortedBack[0]['obj'].id
    #                     ,her_outbound_id=herSortedOut[0]['obj'].id,her_return_id=herSortedBack[0]['obj'].id)
    # session.add(dbWeekend)
    # session.commit()
out=[]
back=[]
if __name__=="__main__":

    #fetchWeekend(datetime(2019,3,22))
    out,back=getRoundTrip("LAX","SFO",datetime(2019,3,22),datetime(2019,3,25),returnObject=True)


    # for i in range(1):
    #     fetchMyWeekend(datetime(2019,2,15)+timedelta(days=i*7))
    #     fetchHerWeekend(datetime(2019,2,15)+timedelta(days=i*7))
#     main()
# with open("card.html","r") as inFile:
#     print(parseCard(inFile.read()),)
