from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import exc
from sqlalchemy.orm.exc import *
from flask import current_app


from config import RTS_SQL_SERVER_CONN, CDMO_SQL_SERVER_CONN

Base = declarative_base()

def get_class_by_tablename(tablename):
    """Return class reference mapped to table. Since the WQ, Met and Nut tables all have the same schema,
    we use the class factory to build the class with the correct tablename. To avoid creating a table object multiple
    times, we use this function to see if the table mapping exists and if so, returns it.

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    table_obj = None
    for c in Base.registry._class_registry.values():
    #for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            table_obj = c
            break
    return table_obj

class cdmo_db:
    def __init__(self):
        self.dbEngine = None
        self.metadata = None
        self.Session = None
        self.connection = None
        self._logger = None

    '''
    def __del__(self):
        try:
            if self.Session is not None:
                self.Session.close()
            if self.connection is not None:
                self.connection.close()
            if self.dbEngine is not None:
                self.dbEngine.dispose()
        except Exception as e:
            current_app.logger.exception(e)
    '''
    def connectDB(self, connect_string, logger, printSQL=False):
        try:
            # Connect to the database
            self.dbEngine = create_engine(connect_string, echo=printSQL)

            # metadata object is used to keep information such as datatypes for our table's columns.
            self.metadata = MetaData()
            self.metadata.bind = self.dbEngine

            self.Session = scoped_session(sessionmaker(bind=self.dbEngine))

            self.connection = self.dbEngine.connect()

            return (True)
        except (exc.OperationalError, exc.InterfaceError, Exception) as e:
            logger.exception(e)
        return (False)

    def remove_session(self):
        self.Session.remove()

    def disconnect(self):
        try:
            if self.Session is not None:
                self.Session.close()
            if self.connection is not None:
                self.connection.close()
            if self.dbEngine is not None:
                self.dbEngine.dispose()
        except Exception as e:
            current_app.logger.exception(e)

        '''
        self.Session.close()
        self.connection.close()
        self.dbEngine.dispose()
        '''
