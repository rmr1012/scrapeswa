import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime,timedelta
import sqlalchemy.exc
try:
    engine = create_engine(os.environ['SWADBSECRET'])
except KeyError:
    engine = create_engine('sqlite:///swa.db')
Base = declarative_base()

class Flight(Base):
    __tablename__ = 'flight'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True,nullable=False)
    flight = Column(Integer, nullable=False)
    src = Column(String(3), nullable=False)
    dst = Column(String(3), nullable=False)
    leave = Column(DateTime,nullable=False)
    arrive = Column(DateTime,nullable=False)
    econAval = Column(Boolean, default=True, nullable=False)
    anytime_fare = Column(Integer)
    anytime_earn = Column(Integer)
    anytime_pts = Column(Integer)
    anytime_epd = Column(Float)
    anytime_ppd = Column(Float)
    economy_fare = Column(Integer)
    economy_earn = Column(Integer)
    economy_pts = Column(Integer)
    economy_epd = Column(Float)
    economy_ppd = Column(Float)
    time_searched = Column(DateTime, default=datetime.now)
    def meta(self):
        return "flight {0}: leaving {1} at {2}, arriving {3} at {4}".format(self.flight, self.src, self.leave, self.dst, self.arrive)
    def price(self):
        if self.econAval:
            return "Fare:{0}(or {1}pts), earning {3} pts".format(self.economy_fare,self.economy_pts,self.economy_earn)
        else:
            return "Fare:{0}(or {1}pts), earning {3} pts".format(self.anytime_fare,self.anytime_pts,self.anytime_earn)
    def __str__(self):
        return self.meta()+"\n"+self.price()
    def __repr__(self):
        return self.__str__()
    def __unicode__(self):
        return self.__str__()


class Weekend(Base):
    __tablename__ = 'weekend'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    friday=Column(DateTime,nullable=False)
    my_outbound_id = Column(Integer, ForeignKey('flight.id'))
    my_outbound = relationship(Flight, foreign_keys=[my_outbound_id])
    my_return_id = Column(Integer, ForeignKey('flight.id'))
    my_return = relationship(Flight, foreign_keys=[my_return_id])
    my_total= Column(Integer)
    her_outbound_id = Column(Integer, ForeignKey('flight.id'))
    her_outbound = relationship(Flight, foreign_keys=[her_outbound_id])
    her_return_id = Column(Integer, ForeignKey('flight.id'))
    her_return = relationship(Flight, foreign_keys=[her_return_id])
    her_total= Column(Integer)
    time_searched = Column(DateTime, default=datetime.now)
