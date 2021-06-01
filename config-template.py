import os

SECRET_API_KEY = os.urandom((32))
PRODUCTION_MACHINE = True
USE_PRODUCTION_DATABASES = True

if PRODUCTION_MACHINE:
    LOGFILE = 'C:\\temp\\rest_data.log'
else:
    LOGFILE = './rest_data.log'

#IN the connection strings, replace the <replace .....> with the appropriate host, user and password.
if PRODUCTION_MACHINE:
    import urllib

    if USE_PRODUCTION_DATABASES:
        RTS_QUOTED = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<replace with server ip>;DATABASE=RTS;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        RTS_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(RTS_QUOTED)
        CDMO_QUOTED = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<replace with server ip>;DATABASE=CDMO;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        CDMO_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(CDMO_QUOTED)
    else:
        RTS_QUOTED = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<replace with server ip>;DATABASE=RTS;UID=odbcrtsremote;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        RTS_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(RTS_QUOTED)
        CDMO_QUOTED = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<replace with server ip>;DATABASE=CDMO;UID=odbcrtsremote;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        CDMO_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(CDMO_QUOTED)
else:
    import urllib

    if USE_PRODUCTION_DATABASES:
        RTS_QUOTED = urllib.parse.quote_plus('DRIVER=FreeTDS;SERVER=<replace with server ip>;DATABASE=RTS;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        RTS_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(RTS_QUOTED)
        CDMO_QUOTED = urllib.parse.quote_plus('DRIVER=FreeTDS;SERVER=<replace with server ip>;DATABASE=CDMO;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        CDMO_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(CDMO_QUOTED)
    else:
        RTS_QUOTED = urllib.parse.quote_plus('DRIVER=FreeTDS;SERVER=<replace with server ip>;DATABASE=RTS;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        RTS_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(RTS_QUOTED)
        CDMO_QUOTED = urllib.parse.quote_plus('DRIVER=FreeTDS;SERVER=<replace with server ip>;DATABASE=CDMO_Test;UID=<replace with DB username>;PWD=<replace with password>;TDS_Version=8.0;Port=1433;')
        CDMO_SQL_SERVER_CONN = 'mssql+pyodbc:///?odbc_connect={}'.format(CDMO_QUOTED)

#Mappings from cellular carrier to the email address to send text messages for a given telephone number.
CELL_CARRIER_EMAIL_HOSTS = {
    'AT&T': 'txt.att.net',
    'T-Mobile': 'tmomail.net',
    'Sprint': 'messaging.sprintpcs.com',
    'Verizon': 'vtext.com'
}