# DEPRECIATED
SWS has upgraded their website to reject non-human agents. This library currently doesn't work. If you are interested to make it work again, please help with the hack and submit a pull request.

# A Simple Scraper for Southwest Airlines

Southwest doesn't provide a direct API to inquire their fares. Other flight fare APIs exist but most are paywalled. This simple scraper simply generate a URL for southwest's web UI and scraps its contents for information. Of course, doing this is rather slow(5-10s per scrape depending on your machine), but for most people who are only interested to automate some simple price checks, a few times day is more than enough. I have not noticed any anti-scraping or CAPTCHA on their site, so we can scrape forever in theory.

Have a great time scraping!

-dr
## Requirements
Python3

Chrome Web Driver - get it here http://chromedriver.chromium.org/downloads

See requirements.txt for python packages used, you don't need to worry about these if you use pip to install 
## Installation
```
pip install scrapeswa
```
## Example Usage
### Import
```
from datetime import datetime
import scrapeswa as sswa
```

### Get Round Trip (object, recommended)
```
>>> outbound, return = sswa.getRoundTrip('LAX','SFO',datetime(2019,5,5),datetime(2019,5,10),returnObject=True)
```

Returns two list of outbound and return of flight object

```
>>> outbound
([<scrapeswa.scrapeswa.SWAFlight object at 0x102f35fd0>, <scrapeswa.scrapeswa.SWAFlight object at 0x102f3d0f0>, ... <scrapeswa.scrapeswa.SWAFlight object at 0x102f3de10>])
```

Accessing information within flight objects

```
>>> outbound[0].__dict__
{'flight': '2994', 'src': 'LAX', 'dst': 'SFO', 'economy': <scrapeswa.scrapeswa.Fare object at 0x102bac198>, 'anytime': <scrapeswa.scrapeswa.Fare object at 0x102bac208>, 'business': <scrapeswa.scrapeswa.Fare object at 0x102bac1d0>, 'leave': datetime.datetime(2019, 5, 5, 6, 45), 'arrive': datetime.datetime(2019, 5, 5, 8, 10)}

outbound[0].economy
<scrapeswa.scrapeswa.Fare object at 0x102bac198>

outbound[0].economy.__dict__
{'flightClass': 'Economy', 'fare': 59, 'earn': 250, 'pts': 3242, 'ppd': 54.94915254237288, 'epd': 4.237288135593221}
```

### Print human readable strings

```
>>> print(outbound[0])
Flight:2994 Leaving LAX Sun 06:45 AM Arriving SFO Sun 08:10 AM
Economy costs $59 (3242pts) earning 250 pts

```
### Fare arithmitic
```
>>> sumFare = outbound[0] + outbound[1]
>>> sumFare
<scrapeswa.scrapeswa.Fare object at 0x102f35f60>
>>> print(sumFare)
Economy costs $134 (7646pts) earning 589 pts
```
## Get Round Trip (dictionary)
```
>>> outbound, return = sswa.getRoundTrip('LAX','SFO',datetime(2019,5,5),datetime(2019,5,10))
```
Returns two list of outbound and return flight info dictionaries
```
([{'Flight': '2994', 'Leave': datetime.datetime(2019, 5, 5, 6, 45), 'Arrive': datetime.datetime(2019, 5, 5, 8, 10), 'src': 'LAX', 'dst': 'SFO', 'bestAval': 'Economy', 'Business': {'fare': 253, 'earn': 2665, 'pts': 17319, 'ppd': 68.45, 'epd': 10.53}, 'Anytime': {'fare': 225, 'earn': 1960, 'pts': 15287, 'ppd': 67.94, 'epd': 8.71}, 'Economy': {'fare': 59, 'earn': 250, 'pts': 3242, 'ppd': 54.94, 'epd': 4.23}},

...

{'Flight': '1077', 'Leave': datetime.datetime(2019, 5, 10, 21, 25), 'Arrive': datetime.datetime(2019, 5, 10, 22, 55), 'src': 'SFO', 'dst': 'LAX', 'bestAval': 'Economy', 'Business': {'fare': 253, 'earn': 2665, 'pts': 17319, 'ppd': 68.45, 'epd': 10.53}, 'Anytime': {'fare': 225, 'earn': 1960, 'pts': 15287, 'ppd': 67.94, 'epd': 8.71}, 'Economy': {'fare': 75, 'earn': 339, 'pts': 4404, 'ppd': 58.72, 'epd': 4.52}}])
```
## Non-pip utilities
If you check out this repository, you will be able to use a few more utilities built based on this tool.

#### checkSW.py
This is a tool I built to figure out who shouhld visit who bwtween my girlfriend and I. If you're in a long distance relationship, this tool could really help you. I'm still working on perfecting the batch scrape ability of this script. Next step is to set it up in crontab to run daily and populate everyday's results in a database, then build a data visualizer to get a good idea of ticket pricing trends and best course of action to see my beloved.

#### models.py
A sqlalchemy ORM built to help orginize the scraped data

#### card.html
A snippet of a single flight card from a fully loaded page. Helps you understand how the scraper is built
