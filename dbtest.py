from models import *
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import sys
#Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session=Session()

testFlight = Flight(flight=1234,src='test1',dst='SFO',leave=datetime(2019,2,20),arrive=datetime(2019,2,21),
econAval=True,anytime_fare=100,anytime_earn=500,anytime_pts=50,economy_pts=1000,economy_fare=150,economy_earn=250)
session.add(testFlight)
testFlight1 = Flight(flight=1234,src='test1',dst='SFO',leave=datetime(2019,2,20),arrive=datetime(2019,2,21),
econAval=True,anytime_fare=100,anytime_earn=500,anytime_pts=50,economy_pts=1000,economy_fare=150,economy_earn=250)
session.add(testFlight1)
testFlight2 = Flight(flight=1234,src='test1',dst='SFO',leave=datetime(2019,2,20),arrive=datetime(2019,2,21),
econAval=True,anytime_fare=100,anytime_earn=500,anytime_pts=50,economy_pts=1000,economy_fare=150,economy_earn=250)
session.add(testFlight2)
testFlight3 = Flight(flight=1234,src='test1',dst='SFO',leave=datetime(2019,2,20),arrive=datetime(2019,2,21),
econAval=True,anytime_fare=100,anytime_earn=500,anytime_pts=50,economy_pts=1000,economy_fare=150,economy_earn=250)
session.add(testFlight3)
session.flush()

testWeekend=Weekend(friday=datetime(2019,3,22),my_outbound_id=testFlight.id,my_return_id=testFlight1.id
                        ,her_outbound_id=testFlight2.id,her_return_id=testFlight3.id)

session.add(testWeekend)


session.commit()

try:
    if sys.argv[1]=="-c":
        Base.metadata.create_all(engine)
except Exception:
    pass
