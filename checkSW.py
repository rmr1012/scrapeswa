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


def fetchWeekend(date):
    mySortedOut,mySortedBack=fetchMyWeekend(date)
    herSortedOut,herSortedBack=fetchHerWeekend(date)

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

    dbWeekend=Weekend(friday=getFriday(date),my_outbound_id=mySortedOut[0]['obj'].id,my_return_id=mySortedBack[0]['obj'].id
                        ,her_outbound_id=herSortedOut[0]['obj'].id,her_return_id=herSortedBack[0]['obj'].id)
    session.add(dbWeekend)
    session.commit()

if __name__=="__main__":

    fetchWeekend(datetime(2019,3,22))



    # for i in range(1):
    #     fetchMyWeekend(datetime(2019,2,15)+timedelta(days=i*7))
    #     fetchHerWeekend(datetime(2019,2,15)+timedelta(days=i*7))
#     main()
# with open("card.html","r") as inFile:
#     print(parseCard(inFile.read()),)
