import requests
import sys
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


def flightFactory(params):
    economyFare=Fare("Economy",params["Economy"]["fare"],params["Economy"]["earn"],params["Economy"]["pts"])
    businessFare=Fare("Business",params["Business"]["fare"],params["Business"]["earn"],params["Business"]["pts"])
    anytimeFare=Fare("Anytime",params["Anytime"]["fare"],params["Anytime"]["earn"],params["Anytime"]["pts"])

    flight=SWAFlight(params["Flight"],params["src"],params["dst"],params["Leave"],params["Arrive"],economyFare,anytimeFare,businessFare)

    return flight
class Fare(object):
    def __init__(self,fltclass,fare,earn,pts):
        self.flightClass=fltclass
        self.fare=fare
        self.earn=earn
        self.pts=pts
        self.ppd=pts/fare
        self.epd=earn/fare
    def getPointValue(self):
        return 1/self.ppd
    def __str__(self):
        return self.flightClass+" costs $"+str(self.fare)+" ("+str(self.pts)+"pts)"+" earning "+str(self.earn)+" pts"

class SWAFlight(object):
    dbid=None
    def __init__(self,flightNum,src,dst,leave,arrive,economyFare,anytimeFare,businessFare):
        self.flight=flightNum
        self.src=src
        self.dst=dst
        self.economy=economyFare
        self.anytime=anytimeFare
        self.business=businessFare
        self.leave=leave
        self.arrive=arrive
    def __str__(self):
        printstr= ''
        printstr+= "Flight:"+str(self.flight)+" Leaving "+self.src+" "+datetime.strftime(self.leave,"%a %I:%M %p")
        printstr+= " Arriving "+self.dst+" "+datetime.strftime(self.arrive,"%a %I:%M %p") + "\n"
        printstr+= str(self.getBestFare())

        return printstr
    def __add__(self, anotherFlight):
        return Fare(self.getBestFare().flightClass,self.getBestFare().fare+anotherFlight.getBestFare().fare,self.getBestFare().earn+anotherFlight.getBestFare().earn,self.getBestFare().pts+anotherFlight.getBestFare().pts)

    def getBestFare(self):
        if self.economy is not None:
            return self.economy
        elif self.anytime is not None:
            return self.anytime
        elif self.business is not None:
            return self.business
        else:
            raise AttributeError("No fare avaliable")


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

def parseCard(soup,date):
    results={'Flight':None,'Leave':None,'Arrive':None,'src':None,'dst':None,'bestAval':'Economy','Business':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Anytime':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Economy':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None}}
    #soup=BeautifulSoup(html,features="lxml")

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
        #print(results)
        return results
            # return(html) # {Flight:123,Leave:Datetime,Arrive:Datetime,bestAval:'Anytime',Business:{fare:None,earn:None,pts:None},Anytime:{fare:120,earn:2500,pts:4500},Economy:{fare:120,earn:2500,pts:4500}}

    except Exception as e:
        pass
        #print("FILED TO PARSE CARD")
        #print(str(e))
        #print(html)

# def main():

def parseCardPts(soup,dataset): # use html to fill in the blank for dataset
    # results={'Flight':None,'Leave':None,'Arrive':None,'bestAval':'Anytime','Business':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Anytime':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None},'Economy':{'fare':None,'earn':None,'pts':None,'ppd':None,'epd':None}}
    #soup=BeautifulSoup(html,features="lxml")
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



def getRoundTrip(src,dst,outDate,returnDate,returnObject=False,mute=True):
    # print("lol")
    # print(progressTotal)
    #holder lists for the flights
    outBound=[]
    returnBound=[]

    #construct SWA website's URL for the search
    url=getSWURL(src,dst,outDate,returnDate)

    ## wail untill page is fully loaded
    driver.get(url)
    timeout = 20
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR,'#air-booking-product-0 div div div div div div span div div fieldset div div .input--text'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        print(url)
        return
    if not mute:
        print("...",end ="")
        sys.stdout.flush()
    # body=driver.find_elements_by_css_selector('body')[0].get_attribute('innerHTML')
    ## get all outbound flight info, grabbing fare info
    body=BeautifulSoup(driver.find_elements_by_css_selector("body")[0].get_attribute('innerHTML'),features="lxml")

    for element in body.select('#air-booking-product-0 div span ul li'):
        outBound+= filter(None, [parseCard(element,outDate)])

    ## get all return flight info, grabbing fare info
    #elements=driver.find_elements_by_css_selector("#air-booking-product-1 div span ul li")
    for element in body.select('#air-booking-product-1 div span ul li'):
        returnBound+= filter(None, [parseCard(element,returnDate)])

    # fill in additional info for the flight dictionary
    for flight in outBound: # designate src and dst
        flight['src']=src
        flight['dst']=dst
    for flight in returnBound:
        flight['src']=dst
        flight['dst']=src

    #### now, fill in the blank for point cost

    url=getSWURL(src,dst,outDate,returnDate,pts=True)
    driver.get(url)

    ## Wait untill page is fully loaded, using this element as a indicator
    timeout = 20
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR,'#air-booking-product-0 div div div div div div span div div fieldset div div .input--text'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")


    if not mute:
        print("...",end ="")
        sys.stdout.flush()

    ## grab all the individual cards for out boud flights
    #elements=driver.find_elements_by_css_selector("#air-booking-product-0 div span ul li")
    body=BeautifulSoup(driver.find_elements_by_css_selector("body")[0].get_attribute('innerHTML'),features="lxml")

    for element in body.select('#air-booking-product-0 div span ul li'):
        parseCardPts(element , outBound)

    ## grab all the individual cards for return bound flights
    #elements=driver.find_elements_by_css_selector("#air-booking-product-1 div span ul li")
    for element in body.select('#air-booking-product-1 div span ul li'):
        parseCardPts(element , returnBound)

    ## return results
    if returnObject:
        # return SWAFlight Objects
        outBoundObjs=[]
        returnBoundObjs=[]
        for flightDict in outBound:
            outBoundObjs.append(flightFactory(flightDict))
        for flightDict in returnBound:
            returnBoundObjs.append(flightFactory(flightDict))
        return outBoundObjs,returnBoundObjs
    else:
        # return dictionary
        return outBound,returnBound
