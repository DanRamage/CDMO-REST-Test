from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, Boolean, SmallInteger, \
    REAL
from sqlalchemy.orm import mapper
from cdmo_db import Base
"""
RTS Classes
"""
"""
"ATemp","F_ATemp","EC_ATemp",
"RH","F_RH","EC_RH",
"BP","F_BP"
"WSpd","F_WSpd","EC_WSpd",
"Wdir","F_Wdir","EC_Wdir",
"TotPrcp","F_TotPrcp","EC_TotPrcp
"TotPAR","F_TotPAR","EC_TotPAR"
"CumPrcp","F_CumPrcp","EC_CumPrcp
"MaxWSpd",,"F_MaxWSpd","EC_MaxWSpd,"MaxWSpdT",
"TotSoRad","F_TotSoRad,"EC_TotSoRad
"F_Record",
"SDWDir","F_SDWDir","EC_SDWDir"
"""




"""
  class rts_met_table(Base):
    __tablename__ = tablename
    ID	          = Column(Integer, primary_key=True)
    Historical	  = Column(Boolean)
    DateTimeStamp	  = Column(DateTime)
    ATemp	          = Column(Float(precision=3,decimal_return_scale=1))
    F_ATemp	      = Column(SmallInteger)
    RH	          = Column(SmallInteger)
    F_RH	          = Column(SmallInteger)
    BP	          = Column(SmallInteger)
    F_BP	          = Column(SmallInteger)
    WSpd	          = Column(Float(precision=4,decimal_return_scale=1))
    F_WSpd	      = Column(SmallInteger)
    Wdir	          = Column(SmallInteger)
    F_Wdir	      = Column(SmallInteger)
    TotPrcp	      = Column(Float(precision=4,decimal_return_scale=1))
    F_TotPrcp	      = Column(SmallInteger)
    TotPAR	      = Column(Float(precision=6,decimal_return_scale=1))
    F_TotPAR	      = Column(SmallInteger)
    MarkAsDeleted	  = Column(Boolean)
    Frequency	      = Column(SmallInteger)
    ProvisionalPlus = Column(Boolean)
    CumPrcp	      = Column(Float(precision=5,decimal_return_scale=1))
    F_CumPrcp	      = Column(SmallInteger)
    EC_ATemp	      = Column(String(11))
    EC_RH	          = Column(String(11))
    EC_BP	          = Column(String(11))
    EC_WSpd	      = Column(String(11))
    EC_Wdir	      = Column(String(11))
    EC_TotPrcp	  = Column(String(11))
    EC_CumPrcp	  = Column(String(11))
    EC_TotPAR	      = Column(String(11))
    MaxWSpd	      = Column(Float(precision=4,decimal_return_scale=1))
    F_MaxWSpd	      = Column(SmallInteger)
    EC_MaxWSpd	  = Column(String(11))
    MaxWSpdT	      = Column(String(5))
    TotSoRad	      = Column(Integer)
    F_TotSoRad	  = Column(SmallInteger)
    EC_TotSoRad	  = Column(String(11))
    F_Record	      = Column(String(18))
    SDWDir	      = Column(SmallInteger)
    F_SDWDir	      = Column(SmallInteger)
    EC_SDWDir	      = Column(String(11))
    code	          = Column(String(10))
    Station_Code	  = Column(String(10))
    isSWMP	      = Column(String(5))
    LastModifiedDate= Column(DateTime)

    def as_dict(self):
      ret_dict = {}
      for column in self.__table__.columns:
        val = getattr(self, column.name)
        if type(column.type) == DateTime:
          val = val.strftime("%Y-%m-%d %H:%M:%S")
        ret_dict[column.name] = val
      #return {c.name: getattr(self, c.name) for c in self.__table__.columns}
      return ret_dict

  #rts_met_table.__name__ = tablename

  return(rts_met_table)
  """


def met_station_table_factory(tablename):
    '''
    This factory builds a met table dynamically. All the met tables have the same schema, so instead of creating
    multiple classes that are the same except for the __tablename__, we use this factory.
    :param tablename:
    :return:
    '''

    class rts_met_table(Base):
        __tablename__ = tablename

        metadata = MetaData()

        ID = Column(Integer, primary_key=True)
        Historical = Column(Boolean)
        DateTimeStamp = Column(DateTime)
        ATemp = Column(Float(precision=3, decimal_return_scale=1))
        F_ATemp = Column(SmallInteger)
        RH = Column(SmallInteger)
        F_RH = Column(SmallInteger)
        BP = Column(SmallInteger)
        F_BP = Column(SmallInteger)
        WSpd = Column(Float(precision=4, decimal_return_scale=1))
        F_WSpd = Column(SmallInteger)
        Wdir = Column(SmallInteger)
        F_Wdir = Column(SmallInteger)
        TotPrcp = Column(Float(precision=4, decimal_return_scale=1))
        F_TotPrcp = Column(SmallInteger)
        TotPAR = Column(Float(precision=6, decimal_return_scale=1))
        F_TotPAR = Column(SmallInteger)
        MarkAsDeleted = Column(Boolean)
        Frequency = Column(SmallInteger)
        ProvisionalPlus = Column(Boolean)
        CumPrcp = Column(Float(precision=5, decimal_return_scale=1))
        F_CumPrcp = Column(SmallInteger)
        EC_ATemp = Column(String(11))
        EC_RH = Column(String(11))
        EC_BP = Column(String(11))
        EC_WSpd = Column(String(11))
        EC_Wdir = Column(String(11))
        EC_TotPrcp = Column(String(11))
        EC_CumPrcp = Column(String(11))
        EC_TotPAR = Column(String(11))
        MaxWSpd = Column(Float(precision=4, decimal_return_scale=1))
        F_MaxWSpd = Column(SmallInteger)
        EC_MaxWSpd = Column(String(11))
        MaxWSpdT = Column(String(5))
        TotSoRad = Column(Integer)
        F_TotSoRad = Column(SmallInteger)
        EC_TotSoRad = Column(String(11))
        F_Record = Column(String(18))
        SDWDir = Column(SmallInteger)
        F_SDWDir = Column(SmallInteger)
        EC_SDWDir = Column(String(11))
        code = Column(String(10))
        Station_Code = Column(String(10))
        isSWMP = Column(String(5))
        LastModifiedDate = Column(DateTime)

    rts_met_table.__name__ = tablename
    rts_met_table.__qualname__ = tablename

    return rts_met_table
    '''
    metadata = MetaData()
    table_object = Table(tablename, metadata,
                          Column("ID", Integer, primary_key=True),
                          Column("Historical", Boolean),
                          Column("DateTimeStamp", DateTime),
                          Column("ATemp", Float(precision=3 ,decimal_return_scale=1)),
                          Column("F_ATemp", SmallInteger),
                          Column("RH", SmallInteger),
                          Column("F_RH", SmallInteger),
                          Column("BP", SmallInteger),
                          Column("F_BP", SmallInteger),
                          Column("WSpd", Float(precision=4 ,decimal_return_scale=1)),
                          Column("F_WSpd", SmallInteger),
                          Column("Wdir", SmallInteger),
                          Column("F_Wdir", SmallInteger),
                          Column("TotPrcp", Float(precision=4 ,decimal_return_scale=1)),
                          Column("F_TotPrcp", SmallInteger),
                          Column("TotPAR", Float(precision=6 ,decimal_return_scale=1)),
                          Column("F_TotPAR", SmallInteger),
                          Column("MarkAsDeleted", Boolean),
                          Column("Frequency", SmallInteger),
                          Column("ProvisionalPlus", Boolean),
                          Column("CumPrcp", Float(precision=5 ,decimal_return_scale=1)),
                          Column("F_CumPrcp", SmallInteger),
                          Column("EC_ATemp", String(11)),
                          Column("EC_RH", String(11)),
                          Column("EC_BP", String(11)),
                          Column("EC_WSpd", String(11)),
                          Column("EC_Wdir", String(11)),
                          Column("EC_TotPrcp", String(11)),
                          Column("EC_CumPrcp", String(11)),
                          Column("EC_TotPAR", String(11)),
                          Column("MaxWSpd", Float(precision=4 ,decimal_return_scale=1)),
                          Column("F_MaxWSpd", SmallInteger),
                          Column("EC_MaxWSpd", String(11)),
                          Column("MaxWSpdT", String(5)),
                          Column("TotSoRad", Integer),
                          Column("F_TotSoRad", SmallInteger),
                          Column("EC_TotSoRad", String(11)),
                          Column("F_Record", String(18)),
                          Column("SDWDir", SmallInteger),
                          Column("F_SDWDir", SmallInteger),
                          Column("EC_SDWDir", String(11)),
                          Column("code", String(10)),
                          Column("Station_Code", String(10)),
                          Column("isSWMP", String(5)),
                          Column("LastModifiedDate", DateTime)
    )

    class rts_met_table():
      pass

    mapper(rts_met_table, table_object)

    return rts_met_table
    '''


def wq_station_table_factory(tablename):
    '''
    This factory builds a wq table dynamically. All the wq tables have the same schema, so instead of creating
    multiple classes that are the same except for the __tablename__, we use this factory.
    :param tablename:
    :return:
    '''

    class rts_wq_table(Base):
        __tablename__ = tablename

        metadata = MetaData()

        ID = Column(Integer, primary_key=True)
        Historical = Column(Boolean)
        DateTimeStamp = Column(DateTime)
        Temp = Column(Float(precision=3, decimal_return_scale=1))
        F_Temp = Column(SmallInteger)
        SpCond = Column(Float(precision=6, decimal_return_scale=2))
        F_SpCond = Column(SmallInteger)
        Sal = Column(Float(precision=4, decimal_return_scale=1))
        F_Sal = Column(SmallInteger)
        DO_pct = Column(Float(precision=4, decimal_return_scale=1))
        F_DO_pct = Column(SmallInteger)
        DO_mgl = Column(Float(precision=4, decimal_return_scale=1))
        F_DO_mgl = Column(SmallInteger)
        Depth = Column(Float(precision=4, decimal_return_scale=2))
        F_Depth = Column(SmallInteger)
        pH = Column(Float(precision=3, decimal_return_scale=1))
        F_pH = Column(SmallInteger)
        Turb = Column(Integer)
        F_Turb = Column(SmallInteger)
        ChlFluor = Column(Float(precision=4, decimal_return_scale=2))
        F_ChlFluor = Column(SmallInteger)
        ProvisionalPlus = Column(Boolean)
        EC_Temp = Column(String(11))
        EC_SpCond = Column(String(11))
        EC_Sal = Column(String(11))
        EC_DO_pct = Column(String(11))
        EC_DO_mgl = Column(String(11))
        EC_Depth = Column(String(11))
        EC_pH = Column(String(11))
        EC_Turb = Column(String(11))
        EC_ChlFluor = Column(String(11))
        F_Record = Column(String(18))
        Level = Column(Float(precision=4, decimal_return_scale=2))
        F_Level = Column(SmallInteger)
        EC_Level = Column(String(11))
        Station_Code = Column(String(10))
        cDepth = Column(Float(precision=4, decimal_return_scale=2))
        cLevel = Column(Float(precision=4, decimal_return_scale=2))
        F_cDepth = Column(SmallInteger)
        F_cLevel = Column(SmallInteger)
        Vented = Column(SmallInteger)
        EC_cDepth = Column(String(11))
        EC_cLevel = Column(String(11))
        isSWMP = Column(String(5))
        LastModifiedDate = Column(DateTime)

    rts_wq_table.__name__ = tablename
    rts_wq_table.__qualname__ = tablename

    return rts_wq_table

    '''
    metadata = MetaData()
    table_object = Table(tablename, metadata,
                         Column("ID", Integer, primary_key=True),
                         Column("Historical", Boolean),
                         Column("DateTimeStamp", DateTime),
                         Column("Temp", Float(precision=3, decimal_return_scale=1)),
                         Column("F_Temp", SmallInteger),
                         Column("SpCond", Float(precision=6, decimal_return_scale=2)),
                         Column("F_SpCond", SmallInteger),
                         Column("Sal", Float(precision=4, decimal_return_scale=1)),
                         Column("F_Sal", SmallInteger),
                         Column("DO_pct", Float(precision=4, decimal_return_scale=1)),
                         Column("F_DO_pct", SmallInteger),
                         Column("DO_mgl", Float(precision=4, decimal_return_scale=1)),
                         Column("F_DO_mgl", SmallInteger),
                         Column("Depth", Float(precision=4, decimal_return_scale=2)),
                         Column("F_Depth", SmallInteger),
                         Column("pH", Float(precision=3, decimal_return_scale=1)),
                         Column("F_pH", SmallInteger),
                         Column("Turb", Integer),
                         Column("F_Turb", SmallInteger),
                         Column("ChlFluor", Float(precision=4, decimal_return_scale=2)),
                         Column("F_ChlFluor", SmallInteger),
                         Column("ProvisionalPlus", Boolean),
                         Column("EC_Temp", String(11)),
                         Column("EC_SpCond", String(11)),
                         Column("EC_Sal", String(11)),
                         Column("EC_DO_pct", String(11)),
                         Column("EC_DO_mgl", String(11)),
                         Column("EC_Depth", String(11)),
                         Column("EC_pH", String(11)),
                         Column("EC_Turb", String(11)),
                         Column("EC_ChlFluor", String(11)),
                         Column("F_Record", String(18)),
                         Column("Level", Float(precision=4, decimal_return_scale=2)),
                         Column("F_Level", SmallInteger),
                         Column("EC_Level", String(11)),
                         Column("Station_Code", String(10)),
                         Column("cDepth", Float(precision=4, decimal_return_scale=2)),
                         Column("cLevel", Float(precision=4, decimal_return_scale=2)),
                         Column("F_cDepth", SmallInteger),
                         Column("F_cLevel", SmallInteger),
                         Column("Vented", SmallInteger),
                         Column("EC_cDepth", String(11)),
                         Column("EC_cLevel", String(11)),
                         Column("isSWMP", String(5)),
                         Column("LastModifiedDate", DateTime)
                         )

    class rts_wq_table():
        pass

    mapper(rts_wq_table, table_object)

    return rts_wq_table
    '''

def nut_station_table_factory(tablename):
    '''
    This factory builds a nut table dynamically. All the nut tables have the same schema, so instead of creating
    multiple classes that are the same except for the __tablename__, we use this factory.
    :param tablename:
    :return:
    '''
    metadata = MetaData()
    column_list = [
        Column("ID", Integer, primary_key=True),
        Column("Historical", Boolean),
        Column("DateTimeStamp", DateTime),
        Column("CollMethd", String(10)),
        Column("REP", String(10)),
        Column("PO4F_C", String(20)),
        Column("PO4F", REAL),
        Column("F_PO4F", SmallInteger),
        Column("DOP_C", String(20)),
        Column("DOP", REAL),
        Column("F_DOP", SmallInteger),
        Column("TDP_C", String(20)),
        Column("TDP", REAL),
        Column("F_TDP", SmallInteger),
        Column("TP_C", String(20)),
        Column("TP", REAL),
        Column("F_TP", SmallInteger),
        Column("PHOSP_C", String(20)),
        Column("PHOSP", REAL),
        Column("F_PHOSP", SmallInteger),
        Column("NH4F_C", String(20)),
        Column("NH4F", REAL),
        Column("F_NH4F", SmallInteger),
        Column("NO2F_C", String(20)),
        Column("NO2F", REAL),
        Column("F_NO2F", SmallInteger),
        Column("NO3F_C", String(20)),
        Column("NO3F", REAL),
        Column("F_NO3F", SmallInteger),
        Column("NO23F_C", String(20)),
        Column("NO23F", REAL),
        Column("F_NO23F", SmallInteger),
        Column("DIN_C", String(20)),
        Column("DIN", REAL),
        Column("F_DIN", SmallInteger),
        Column("DON_C", String(20)),
        Column("DON", REAL),
        Column("F_DON", SmallInteger),
        Column("TDN_C", String(20)),
        Column("TDN", REAL),
        Column("F_TDN", SmallInteger),
        Column("TN_C", String(20)),
        Column("TN", REAL),
        Column("F_TN", SmallInteger),
        Column("TKN_C", String(20)),
        Column("TKN", REAL),
        Column("F_TKN", SmallInteger),
        Column("TKNF_C", String(20)),
        Column("TKNF", REAL),
        Column("F_TKNF", SmallInteger),
        Column("TON_C", String(20)),
        Column("TON", REAL),
        Column("F_TON", SmallInteger),
        Column("PON_C", String(20)),
        Column("PON", REAL),
        Column("F_PON", SmallInteger),
        Column("PN_C", String(20)),
        Column("PN", REAL),
        Column("F_PN", SmallInteger),
        Column("CHLA_N_C", String(20)),
        Column("CHLA_N", REAL),
        Column("F_CHLA_N", SmallInteger),
        Column("PHEA_C", String(20)),
        Column("PHEA", REAL),
        Column("F_PHEA", SmallInteger),
        Column("TOC_C", String(20)),
        Column("TOC", REAL),
        Column("F_TOC", SmallInteger),
        Column("DOC_C", String(20)),
        Column("DOC", REAL),
        Column("F_DOC", SmallInteger),
        Column("POC_C", String(20)),
        Column("POC", REAL),
        Column("F_POC", SmallInteger),
        Column("TSS_C", String(20)),
        Column("TSS", REAL),
        Column("F_TSS", SmallInteger),
        Column("TVS_C", String(20)),
        Column("TVS", REAL),
        Column("F_TVS", SmallInteger),
        Column("TFS_C", String(20)),
        Column("TFS", REAL),
        Column("F_TFS", SmallInteger),
        Column("WTEM_N_C", String(20)),
        Column("WTEM_N", REAL),
        Column("F_WTEM_N", SmallInteger),
        Column("SCON_N_C", String(20)),
        Column("SCON_N", REAL),
        Column("F_SCON_N", SmallInteger),
        Column("SALT_N_C", String(20)),
        Column("SALT_N", REAL),
        Column("F_SALT_N", SmallInteger),
        Column("DO_N_C", String(20)),
        Column("DO_N", REAL),
        Column("F_DO_N", SmallInteger),
        Column("DO_S_N_C", String(20)),
        Column("DO_S_N", REAL),
        Column("F_DO_S_N", SmallInteger),
        Column("PH_N_C", String(20)),
        Column("PH_N", REAL),
        Column("F_PH_N", SmallInteger),
        Column("TURB_N_C", String(20)),
        Column("TURB_N", REAL),
        Column("F_TURB_N", SmallInteger),
        Column("COLOR_C", String(20)),
        Column("COLOR", REAL),
        Column("F_COLOR", SmallInteger),
        Column("TDEP_N_C", String(20)),
        Column("TDEP_N", REAL),
        Column("F_TDEP_N", SmallInteger),
        Column("SiO4F_C", String(20)),
        Column("SiO4F", REAL),
        Column("F_SiO4F", SmallInteger),
        Column("SECCHI_C", String(20)),
        Column("SECCHI", REAL),
        Column("F_SECCHI", SmallInteger),
        Column("IRR0_N_C", String(20)),
        Column("IRR0_N", REAL),
        Column("F_IRR0_N", SmallInteger),
        Column("IRR1_N_C", String(20)),
        Column("IRR1_N", REAL),
        Column("F_IRR1_N", SmallInteger),
        Column("IRR2_N_C", String(20)),
        Column("IRR2_N", REAL),
        Column("F_IRR2_N", SmallInteger),
        Column("Ke_N_C", String(20)),
        Column("Ke_N", REAL),
        Column("F_Ke_N", SmallInteger),
        Column("ATEM_N_C", String(20)),
        Column("ATEM_N", REAL),
        Column("F_ATEM_N", SmallInteger),
        Column("CLOUD_C", String(20)),
        Column("CLOUD", REAL),
        Column("F_CLOUD", SmallInteger),
        Column("PRECIP_C", String(20)),
        Column("PRECIP", REAL),
        Column("F_PRECIP", SmallInteger),
        Column("TIDE_C", String(20)),
        Column("TIDE", REAL),
        Column("F_TIDE", SmallInteger),
        Column("WAVHGT_C", String(20)),
        Column("WAVHGT", REAL),
        Column("F_WAVHGT", SmallInteger),
        Column("WINDIR_C", String(20)),
        Column("WINDIR", REAL),
        Column("F_WINDIR", SmallInteger),
        Column("WINSPD_C", String(20)),
        Column("WINSPD", REAL),
        Column("F_WINSPD", SmallInteger),
        Column("MarkAsDeleted", Boolean),
        Column("UREA_F", Float),
        Column("UREA_F_C", String(20)),
        Column("F_UREA_F", SmallInteger),
        Column("ProvisionalPlus", Boolean),
        Column("F_Record", String(47)),
        Column("EC_PO4F", String(11)),
        Column("EC_DOP", String(11)),
        Column("EC_TDP", String(11)),
        Column("EC_TP", String(11)),
        Column("EC_PHOSP", String(11)),
        Column("EC_NH4F", String(11)),
        Column("EC_NO2F", String(11)),
        Column("EC_NO3F", String(11)),
        Column("EC_NO23F", String(11)),
        Column("EC_DIN", String(11)),
        Column("EC_DON", String(11)),
        Column("EC_TDN", String(11)),
        Column("EC_TN", String(11)),
        Column("EC_TKN", String(11)),
        Column("EC_TKNF", String(11)),
        Column("EC_TON", String(11)),
        Column("EC_PON", String(11)),
        Column("EC_PN", String(11)),
        Column("EC_CHLA_N", String(11)),
        Column("EC_TCHL_N", String(11)),
        Column("EC_FCHL_N", String(11)),
        Column("EC_PHEA", String(11)),
        Column("EC_TOC", String(11)),
        Column("EC_DOC", String(11)),
        Column("EC_POC", String(11)),
        Column("EC_TSS", String(11)),
        Column("EC_TVS", String(11)),
        Column("EC_TFS", String(11)),
        Column("EC_WTEM_N", String(11)),
        Column("EC_SCON_N", String(11)),
        Column("EC_SALT_N", String(11)),
        Column("EC_DO_N", String(11)),
        Column("EC_DO_S_N", String(11)),
        Column("EC_PH_N", String(11)),
        Column("EC_TURB_N", String(11)),
        Column("EC_COLOR", String(11)),
        Column("EC_TDEP_N", String(11)),
        Column("EC_SiO4F", String(11)),
        Column("EC_SECCHI", String(11)),
        Column("EC_IRR0_N", String(11)),
        Column("EC_IRR1_N", String(11)),
        Column("EC_IRR2_N", String(11)),
        Column("EC_Ke_N", String(11)),
        Column("EC_ATEM_N", String(11)),
        Column("EC_CLOUD", String(11)),
        Column("EC_PRECIP", String(11)),
        Column("EC_TIDE", String(11)),
        Column("EC_WAVHGT", String(11)),
        Column("EC_WINDIR", String(11)),
        Column("EC_WINSPD", String(11)),
        Column("EC_SRPF", String(11)),
        Column("EC_SRP", String(11)),
        Column("EC_UREA_F", String(11)),
        Column("UncCHLa_N_C", String(20)),
        Column("UncCHLa_N", REAL),
        Column("F_UncCHLa_N", SmallInteger),
        Column("EC_UncCHLa_N", String(11)),
        Column("Station_Code", String(50)),
        Column("Kd_N", REAL),
        Column("F_Kd_N", SmallInteger),
        Column("EC_Kd_N", String(11)),
        Column("Kd_N_C", String(20)),
        Column("SO4", REAL),
        Column("F_SO4", SmallInteger),
        Column("EC_SO4", String(11)),
        Column("Cl", REAL),
        Column("F_Cl", SmallInteger),
        Column("EC_Cl", String(11)),
        Column("adjustedDateTimeStamp", DateTime),
        Column("isSWMP", String(5)),
        Column("LastModifiedDate", DateTime),
        Column("TOTCOL_CFU", REAL),
        Column("F_TOTCOL_CFU", SmallInteger),
        Column("EC_TOTCOL_CFU", String(20)),
        Column("FECCOL_CFU", REAL),
        Column("F_FECCOL_CFU", SmallInteger),
        Column("EC_FECCOL_CFU", String(11)),
        Column("ECOLI_CFU", String(20)),
        Column("F_ECOLI_CFU", SmallInteger),
        Column("EC_ECOLI_CFU", String(20)),
        Column("ENTERO_CFU", REAL),
        Column("F_ENTERO_CFU", SmallInteger),
        Column("EC_ENTERO_CFU", String(20)),
        Column("ENTFEC_CFU", String(20)),
        Column("F_ENTFEC_CFU", SmallInteger),
        Column("EC_ENTFEC_CFU", SmallInteger),
        Column("TOTCOL_MPN", REAL),
        Column("F_TOTCOL_MPN", SmallInteger),
        Column("EC_TOTCOL_MPN", String(20)),
        Column("ECOLI_MPN", String(20)),
        Column("F_ECOLI_MPN", SmallInteger),
        Column("EC_ECOLI_MPN", String(20)),
        Column("ENTERO_MPN", REAL),
        Column("F_ENTERO_MPN", SmallInteger),
        Column("EC_ENTERO_MPN", String(20)),
        Column("ENTFEC_MPN", String(20)),
        Column("F_ENTFEC_MPN", SmallInteger),
        Column("EC_ENTFEC_MPN", String(20)),
        Column("FECCOL_MPN", REAL),
        Column("F_FECCOL_MPN", SmallInteger),
        Column("EC_FECCOL_MPN", String(20)),
        Column("TOTCOL_CFU_C", String(20)),
        Column("FECCOL_CFU_C", String(20)),
        Column("ECOLI_CFU_C", String(20)),
        Column("ENTERO_CFU_C", String(20)),
        Column("ENTFEC_CFU_C", String(20)),
        Column("TOTCOL_MPN_C", String(20)),
        Column("FECCOL_MPN_C", String(20)),
        Column("ECOLI_MPN_C", String(20)),
        Column("ENTERO_MPN_C", String(20)),
        Column("ENTFEC_MPN_C", String(20))
    ]
    table_object = Table(tablename, metadata, *column_list)

    class rts_nut_table():
        pass

    mapper(rts_nut_table, table_object)

    return rts_nut_table