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

def fetchWeekend(weekof,srcs,dsts):
    friday=getFriday(weekof)
    saturday=friday+timedelta(days=1)
    sunday=saturday+timedelta(days=1)
    monday=sunday+timedelta(days=1)

    if type(srcs) is not type([]):
        srcs=[srcs]
    if type(dsts) is not type([]):
        dsts=[dsts]

    print("Checking flights for the weekend of ")
    print(datetime.strftime(friday,"%a %b %d %Y" ))

    # iterate though all the possible destination combinations
    allOut=[]
    allBack=[]
    for src in srcs:
        for dst in dsts:
            FridayOut,SundayBack=getRoundTrip(src,dst,friday,sunday,returnObject=True)
            SaturdayOut,MondayBack=getRoundTrip(src,dst,saturday,monday,returnObject=True)
            allOut+=FridayOut+SaturdayOut
            allBack+=SundayBack+MondayBack

    filteredOut=[]
    filteredReturn=[]
    for flight in allOut:
        if flight.leave>=friday.replace(hour=19,minute=29) and flight.arrive<saturday.replace(hour=11,minute=30):
            filteredOut.append(flight)
    for flight in allBack:
        if flight.leave>=sunday.replace(hour=19,minute=00) and flight.arrive<monday.replace(hour=9,minute=45):
            filteredReturn.append(flight)
    sortedOut = sorted(filteredOut,key=lambda x: x.getBestFare().fare)
    sortedBack = sorted(filteredReturn,key=lambda x: x.getBestFare().fare)
    #print(sortedOut)
    #print(sortedBack)
    if(sortedOut is not None and sortedBack is not None):
        return sortedOut,sortedBack


def dbAddFlight(flight):
    dbflight = Flight(flight=flight.flight,src=flight.src,dst=flight.dst,leave=flight.leave,arrive=flight.arrive,
    econAval=flight.getBestFare().flightClass=="Economy",anytime_fare=flight.anytime.fare,anytime_earn=flight.anytime.earn,
    anytime_pts=flight.anytime.pts,economy_pts=flight.economy.pts,economy_fare=flight.economy.fare,economy_earn=flight.economy.earn)
    session.add(dbflight)
    session.flush()
    flight.dbid=dbflight.id
    session.commit()
def dbAddFlights(flights):
    for flight in flights:
        dbAddFlight(flight)
def dbAddWeekend(date,mySortedOut,mySortedBack,herSortedOut,herSortedBack):
    dbAddFlights(mySortedOut+mySortedBack+herSortedOut+herSortedBack)
    myTotal=mySortedOut[0].getBestFare().fare+mySortedBack[0].getBestFare().fare
    herTotal=herSortedOut[0].getBestFare().fare+herSortedBack[0].getBestFare().fare
    dbWeekend=Weekend(friday=datetime(2019,3,22),my_outbound_id=mySortedOut[0].dbid,my_return_id=mySortedBack[0].dbid
                            ,her_outbound_id=herSortedOut[0].dbid,her_return_id=herSortedOut[0].dbid,
                            my_total=myTotal,her_total=herTotal)
    session.add(dbWeekend)
    session.commit()

if __name__=="__main__":

    # out,back=fetchWeekend(datetime(2019,3,22))
    date=datetime(2019,3,22)
    friday=getFriday(date)
    mySortedOut,mySortedBack=fetchWeekend(date,['SFO','SJC'],['LAX'],)
    bo=mySortedOut[0]
    br=mySortedBack[0]
    print(color("Your Best Bet for the Weekend of "+datetime.strftime(friday,"%a %b %d %Y" )+" is...",'green'))
    print(color(str(bo),'blue'))
    print(color(str(br),'blue'))
    print(color(str(bo+br),'orange'))
    #print(color("Total: $"+str(bo.getBestFare().fare+br.getBestFare().fare)+"or("+str(bo.getBestFare().pts+br.getBestFare().pts)+" pts), earning "+str(bo.getBestFare().earn+br.getBestFare().earn)+"pts",'yeloow'))

    herSortedOut,herSortedBack=fetchWeekend(date,['LAX'],['SFO','SJC'])
    hbo=herSortedOut[0]
    hbr=herSortedBack[0]
    print(color("Her Best Bet for the Weekend of "+datetime.strftime(friday,"%a %b %d %Y" )+" is...",'green'))
    print(color(str(hbo),'blue'))
    print(color(str(hbr),'blue'))
    print(color(str(hbo+hbr),'orange'))
    #print(color("Total: $"+str(hbo.getBestFare().fare+hbr.getBestFare().fare)+"or("+str(hbo.getBestFare().pts+hbr.getBestFare().pts)+" pts), earning "+str(hbo.getBestFare().earn+hbr.getBestFare().earn)+"pts",'yeloow'))

    try:
        dbAddWeekend(friday,mySortedOut,mySortedBack,herSortedOut,herSortedBack)
    except sqlalchemy.exc.OperationalError:
        print("db file empty, creating schema...")
        Base.metadata.create_all(engine)
        print("schema created, writing data...")
        session.rollback()
        dbAddWeekend(friday,mySortedOut,mySortedBack,herSortedOut,herSortedBack)
    #print(color("Total: $"+str(sortedOut[0][sortedOut[0]['bestAval']]['fare'] + sortedBack[0][sortedBack[0]['bestAval']]['fare'])+"(or "+str(sortedOut[0][sortedOut[0]['bestAval']]['pts'] + sortedBack[0][sortedBack[0]['bestAval']]['pts'])+"pts)"+" earning "+str(sortedOut[0][sortedOut[0]['bestAval']]['earn']+sortedBack[0][sortedBack[0]['bestAval']]['earn'])+' pts ','orange'))


    #herSortedOut,herSortedBack=fetchHerWeekend(date,['LAX','LGB'],['SFO','SJC'])

    #out,back=getRoundTrip("LAX","SFO",datetime(2019,3,22),datetime(2019,3,25),returnObject=True)


    # for i in range(1):
    #     fetchMyWeekend(datetime(2019,2,15)+timedelta(days=i*7))
    #     fetchHerWeekend(datetime(2019,2,15)+timedelta(days=i*7))
#     main()
# with open("card.html","r") as inFile:
#     print(parseCard(inFile.read()),)
