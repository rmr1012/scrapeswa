from models import *
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import sys
#Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session=Session()

testFlight = Flight(flight=1234,src='LAX',dst='SFO',leave=datetime(2019,2,20),arrive=datetime(2019,2,21),
econAval=True,anytime_fare=100,anytime_earn=500,anytime_pts=50,economy_pts=1000,economy_fare=150,economy_earn=250)
session.add(testFlight)

if sys.argv[1]=="-c":
    Base.metadata.create_all(engine)
