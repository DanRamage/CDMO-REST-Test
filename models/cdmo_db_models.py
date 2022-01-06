from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, Boolean, Text, SmallInteger, \
    REAL
import jwt
from cdmo_db import Base

"""
CDMO database
"""


class web_services_tracking(Base):
    __tablename__ = 'webservicesTracking'
    DateTimeStamp = Column(DateTime)
    ip = Column(String(50))
    stationCode = Column(String(10))
    functionCalled = Column(String(100))
    paramCalled = Column(String(500))
    dateOne = Column(String(50))
    dateTwo = Column(String(50))
    recs = Column(Integer)
    id = Column(Integer, primary_key=True)


class mobile_web_services_tracking(Base):
    __tablename__ = 'mobileTracking'
    id = Column(Integer, primary_key=True)
    stationCode = Column(String(50))
    DateTimeStamp = Column(DateTime)
    osInfo = Column(Text())

Sampling_Station_API_Allowed_Columns = ["NERR_Site_ID",
                                        "Station_Code",
                                        "Station_Name",
                                        #"Latitude",
                                        #"Longitude",
                                        "Status",
                                        "Active_Dates",
                                        "Real_Time"
                                        "GMT_Offset",
                                        "Station_Type",
                                        "Params_Reported",
                                        "State",
                                        "Reserve_Name",
                                        "isSWMP",
                                        "HADS_ID"]
class Sampling_Station(Base):
    __tablename__ = 'Sampling_Stations'
    ID = Column(Integer, primary_key=True)
    NERR_Site_ID = Column(String(50))
    Station_Code = Column(String(10))
    Station_Name = Column(String(40))
    Lat_Long = Column(String(50))
    Latitude = Column(String(50))
    Longitude = Column(String(50))
    Status = Column(String(10))
    Active_Dates = Column(String(50))
    Real_Time = Column(String(10))
    HADS_ID = Column(String(10))
    GMT_Offset = Column(String(10))
    Station_Type = Column(SmallInteger)
    Region = Column(SmallInteger)
    Params_Reported = Column(String(300))
    Report_Errors = Column(Boolean)
    State = Column(String(10))
    Reserve_Name = Column(String(50))
    Vented = Column(SmallInteger)
    Vertical = Column(String(10))
    Active_Dates_From = Column(DateTime)
    Active_Dates_To = Column(DateTime)
    alertValue = Column(Float(precision=6, decimal_return_scale=2))
    alertNumber = Column(String(50))
    alertEmail = Column(String(50))
    activeAlerts = Column(String(10))
    alertEmailOther = Column(String(50))
    alertParam1 = Column(String(50))
    alertValueMin1 = Column(Float(precision=6, decimal_return_scale=2))
    alertValueMax1 = Column(Float(precision=6, decimal_return_scale=2))
    alertParam2 = Column(String(50))
    alertValueMin2 = Column(Float(precision=6, decimal_return_scale=2))
    alertValueMax2 = Column(Float(precision=6, decimal_return_scale=2))
    alertParam3 = Column(String(50))
    alertValueMin3 = Column(Float(precision=6, decimal_return_scale=2))
    alertValueMax3 = Column(Float(precision=6, decimal_return_scale=2))
    changeToFifteen = Column(DateTime)
    isSWMP = Column(String(5))
    def as_dict(self, column_list=None):
        ret_dict = {}
        for column in self.__table__.columns:
            #if column.name in Sampling_Station_API_Allowed_Columns:
            val = getattr(self, column.name)
            #If we are restricting the columns returned, check if column in list, if not don't use it.
            if column_list is not None and column.name not in column_list:
                val = None
            if val is not None:
                if type(column.type) == String:
                    val = val.strip()
                ret_dict[column.name] = val
            #If we are not limiting the returned columns, and the value of the parameter from the DB is None, we
            #still want to send the parameter in the response.
            elif column_list is None:
                ret_dict[column.name] = None
        return ret_dict


class signalStrength(Base):
    __tablename__ = 'signalStrength'

    id = Column(Integer, primary_key=True)
    stationCode = Column(String(50))
    DateTimeStamp = Column(DateTime)
    signalStrength = Column(Float(precision=6, decimal_return_scale=2))
    stationCode = Column(String(50))


class batteryVoltage(Base):
    __tablename__ = 'batteryVoltage'

    DateTimeStamp = Column(DateTime)
    batteryVolts = Column(Float(precision=6, decimal_return_scale=2))
    samplingStation = Column(String(50))
    id = Column(Integer, primary_key=True)

#This table is for the WQ stations at the moment. We decode the actual station voltage as opposed to the
#sonde voltages. The batteryVoltage table above is decoding the battery voltage for WQ passed in the data payload
#which is not necessarily the station voltage.
#We alias the columns so the class members are the same as the batteryVoltage table above.
class StationBatteryVoltage(Base):
  __tablename__ = 'StationBatteryVoltage'

  id = Column("ID", Integer, primary_key=True)
  DateTimeStamp = Column(DateTime)
  samplingStation = Column("SamplingStation", String(16))
  batteryVolts = Column("Voltage", Float())


class NERR_Sites(Base):
    metadata = MetaData()
    __table__ = Table('NERR_Sites', metadata,
                        Column("NERR_Site_ID", String(50), primary_key=True),
                        Column("NERR_Site_Code", String(10), primary_key=True),
                        Column("NERR_Site_Name", String(40)),
                        Column("State", String(10)),
                        Column("IOOS_shortname", String(40)),
                        Column("NOAA Name", String(25)),
                        Column("gisReserveHabitat", String(50)),
                        Column("reserveLatitude", String(50)),
                        Column("reserveLongitude", String(50)))
    def as_dict(self):
        ret_dict = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if val is not None:
                val = val.strip()
            ret_dict[column.name] = val
        return ret_dict

class CDMO_Users(Base):
    metadata = MetaData()
    __table__ = Table('CDMO_Users', metadata,
                      Column("User_name", String(10)),
                      Column("Password", String(10)),
                      Column("CDMO_Access", Boolean()),
                      Column("Reserve_Only", String(3)),
                      Column("id", Integer, primary_key=True))

'''
class NERR_Sites(Base):
    __tablename__ = 'NERR_Sites'
    NERR_Site_ID    = Column(String(50), primary_key=True)
    NERR_Site_Code  = Column(String(10), primary_key=True)
    NERR_Site_Name  = Column(String(40))
    State           = Column(String(10))
    IOOS_shortname  = Column(String(40))
    NOAA Name       = Column(String(25))
    gisReserveHabitat = Column(String(50))
    reserveLatitude = Column(String(50))
    reserveLongitude= Column(String(50))
'''
