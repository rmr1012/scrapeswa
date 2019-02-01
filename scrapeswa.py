
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


def getSWURL(src,dst,outDate,inDate,pts=False):
    endpoint="https://www.southwest.com/air/booking/select.html"

    context={'adultPassengersCount': '1',
            'departureDate': outDate.strftime("%Y-%m-%d") , #format '2019-02-04'
            'departureTimeOfDay': 'ALL_DAY',
            'destinationAirportCode': dst,
            'fareType': 'USD',
            'originationAirportCode': src,
            'passengerType': 'ADULT',
            'reset': 'true',
            'returnDate': inDate.strftime("%Y-%m-%d"),
            'returnTimeOfDay': 'ALL_DAY',
            'seniorPassengersCount': '0',
            'tripType': 'roundtrip'}
    if pts:
        context["fareType"]='POINTS'
    qstr = urlencode(context)
    # str resolves to: 'q=whee%21+Stanford%21%21%21&something=else'
    url = endpoint+"?int=HOMEQBOMAIR&"+qstr
    return url

def parseCard(html,date):
    results={'Flight':None,'Leave':None,'Arrive':None,'src':None,'dst':None,'bestAval':'Economy','Business':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Anytime':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Economy':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None}}
    soup=BeautifulSoup(html,features="lxml")

    try:
        results['Flight']=re.search(r'[0-9]{1,4}',soup.select_one('.flight-numbers--flight-number .actionable--text').text,re.M).group()
        results["Leave"]=  datetime.strptime(datetime.strftime(date,'%b %d %Y ')+timeRE.search(soup.select('.air-operations-time-status')[0].text.replace('\n', '')).group(), '%b %d %Y %I:%M%p')
        results["Arrive"]=  datetime.strptime(datetime.strftime(date,'%b %d %Y ')+timeRE.search(soup.select('.air-operations-time-status')[1].text.replace('\n', '')).group(), '%b %d %Y %I:%M%p')

        findFarePts = re.compile(r'\$([0-9]{0,4}),[a-z|A-Z|\s]*([0-9]{1,5})', re.MULTILINE)

        for fareType in soup.select('.fare-button--button'):
            infoLabel=str(fareType['aria-label'])
            #print(infoLabel)
            if 'Business' in infoLabel:
                result=findFarePts.search(infoLabel)
                results["Business"]['fare']=int(result.group(1))
                results["Business"]['earn']=int(result.group(2))
            if 'Anytime' in infoLabel:
                result=findFarePts.search(infoLabel)
                results["Anytime"]['fare']=int(result.group(1))
                results["Anytime"]['earn']=int(result.group(2))
            if 'Get Away' in infoLabel:
                result=findFarePts.search(infoLabel)
                results["Economy"]['fare']=int(result.group(1))
                results["Economy"]['earn']=int(result.group(2))
        return results
            # return(html) # {Flight:123,Leave:Datetime,Arrive:Datetime,bestAval:'Anytime',Business:{fare:None,earn:None,pts:None},Anytime:{fare:120,earn:2500,pts:4500},Economy:{fare:120,earn:2500,pts:4500}}

    except Exception as e:
        pass
        #print("FILED TO PARSE CARD")
        #print(str(e))
        #print(html)

# def main():

def parseCardPts(html,dataset): # use html to fill in the blank for dataset
    # results={'Flight':None,'Leave':None,'Arrive':None,'bestAval':'Anytime','Business':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Anytime':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Economy':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None}}
    soup=BeautifulSoup(html,features="lxml")
    rawtxt=soup.text
    #print(rawtxt)
    # try:
    for flight in dataset:
        if "# "+flight['Flight'] in rawtxt:
            for fareType in soup.select('.fare-button--button'):
                #print(fareType.text)
                ptsLabel=int(re.search(r'([0-9]{1,6}) Points',fareType.text).group(1))
                #print(ptsLabel)
                infoLabel=str(fareType['aria-label'])
                #print(infoLabel)
                if 'Business' in infoLabel:
                    flight["Business"]['pts']=ptsLabel
                    flight["Business"]['ppd']=ptsLabel/flight["Business"]['fare']
                    flight["Business"]['epd']=flight["Business"]['earn']/flight["Business"]['fare']
                if 'Anytime' in infoLabel:
                    flight["Anytime"]['pts']=ptsLabel
                    flight["Anytime"]['ppd']=ptsLabel/flight["Anytime"]['fare']
                    flight["Anytime"]['epd']=flight["Anytime"]['earn']/flight["Anytime"]['fare']
                if 'Get Away' in infoLabel:
                    flight["Economy"]['pts']=ptsLabel
                    flight["Economy"]['ppd']=ptsLabel/flight["Economy"]['fare']
                    flight["Economy"]['epd']=flight["Economy"]['earn']/flight["Economy"]['fare']

            # return(html) # {Flight:123,Leave:Datetime,Arrive:Datetime,bestAval:'Anytime',Business:{fare:None,earn:None,pts:None},Anytime:{fare:120,earn:2500,pts:4500},Economy:{fare:120,earn:2500,pts:4500}}

    # except Exception as e:
    #     print(str(e))
    #     pass


def getFriday(date):
    while date.weekday() != 4:
        date+=timedelta(days=1)
    return date



def parseRoundTrip(src,dst,outDate,backDate):

    url=getSWURL(src,dst,outDate,backDate)
    #print(url)
    driver.get(url)
    timeout = 8
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR,'#air-booking-product-0 div div div div div div span div div fieldset div div .input--text'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    #print("proceding")

    elements=driver.find_elements_by_css_selector("#air-booking-product-0 div span ul li")
    Outbound=[]
    for element in elements:
        Outbound+= filter(None, [parseCard(str(element.get_attribute('innerHTML')),outDate)])


    elements=driver.find_elements_by_css_selector("#air-booking-product-1 div span ul li")
    Returnbound=[]
    for element in elements:
        Returnbound+= filter(None, [parseCard(str(element.get_attribute('innerHTML')),backDate)])

    for flight in Outbound: # designate src and dst
        flight['src']=src
        flight['dst']=dst
    for flight in Returnbound:
        flight['src']=dst
        flight['dst']=src

    #### now, fill in the blank for point cost

    url=getSWURL(src,dst,outDate,backDate,pts=True)
    driver.get(url)
    timeout = 10
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR,'#air-booking-product-0 div div div div div div span div div fieldset div div .input--text'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    print("page loaded")

    elements=driver.find_elements_by_css_selector("#air-booking-product-0 div span ul li")
    for element in elements:
        parseCardPts(str(element.get_attribute('innerHTML')) , Outbound)


    elements=driver.find_elements_by_css_selector("#air-booking-product-1 div span ul li")
    for element in elements:
        parseCardPts(str(element.get_attribute('innerHTML')) , Returnbound)


    return Outbound,Returnbound
def fetchWeekend(date):
    mySortedOut,mySortedBack=fetchMyWeekend(date)
    herSortedOut,herSortedBack=fetchHerWeekend(date)

    dbWeekend=Weekend(friday=getFriday(date),my_outbound_id=mySortedOut[0]['obj'].id,my_return_id=mySortedBack[0]['obj'].id
                        ,her_outbound_id=herSortedOut[0]['obj'].id,her_return_id=herSortedBack[0]['obj'].id)
    session.add(dbWeekend)
    session.commit()


    # for i in range(1):
    #     fetchMyWeekend(datetime(2019,2,15)+timedelta(days=i*7))
    #     fetchHerWeekend(datetime(2019,2,15)+timedelta(days=i*7))
#     main()
# with open("card.html","r") as inFile:
#     print(parseCard(inFile.read()),)
