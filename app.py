import json
import os.path
import secrets
from flask import Flask, g, current_app
import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter
import atexit
from datetime import datetime, timedelta
from flask_cors import CORS
from cdmo_db import cdmo_db
from config import (SECRET_API_KEY, SECRET_KEY_FILE, SECRET_KEY_ROTATE_HOURS,
                    RTS_SQL_SERVER_CONN, CDMO_SQL_SERVER_CONN, LOGFILE, PRODUCTION_MACHINE)
import signal

# from apispec import APISpec

rts_db = cdmo_db()
cdmo_db = cdmo_db()


class GracefulKiller:
    kill_now = False

    def __init__(self, rts_db_conn, cdmo_db_conn):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self._rts_db_conn = rts_db_conn
        self._cdmo_db_conn = cdmo_db_conn

    def exit_gracefully(self, signum, frame):
        self._rts_db_conn.disconnect()
        self._cdmo_db_conn.disconnect()
        self.kill_now = True


def init_logging(app):
    app.logger.handlers.clear()
    app.logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(filename=LOGFILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter('%(asctime)s,%(levelname)s,%(module)s,%(funcName)s,%(lineno)d,%(message)s'))
    app.logger.addHandler(file_handler)

    app.logger.debug("Logging initialized")

    return


def build_url_rules(app):
    from rest_views import StationInfoAPI, \
        CMDOAPIHelp, \
        HADSLatestAPI, \
        NERRSitesAPI, \
        NERRStationsInfo, \
        Login, \
        NERRUpdateAlerts, \
        NERRToggleAlerts, \
        NERRReserveStations, \
        NERRDeleteAlerts

    app.logger.debug("build_url_rules started")
    if PRODUCTION_MACHINE:
        app.add_url_rule('/resttest/cdmoapi/help', view_func=CMDOAPIHelp.as_view('help'))

        app.add_url_rule('/resttest/cdmorestdata/<string:station>/data',
                         view_func=StationInfoAPI.as_view('station_info_api'), methods=['GET'])

        app.add_url_rule('/resttest/cdmorestdata/<string:station>/hadsdata',
                         view_func=HADSLatestAPI.as_view('hads_data_api'), methods=['GET'])

        app.add_url_rule('/resttest/cdmorestdata/reserves',
                         view_func=NERRSitesAPI.as_view('nerr_sites_api'), methods=['GET'])

        app.add_url_rule('/resttest/cdmorestdata/<string:reserve>/stations',
                         view_func=NERRReserveStations.as_view('nerr_reserve_stations'), methods=['GET'])

        app.add_url_rule('/resttest/cdmorestdata/stationsmetadata',
                         view_func=NERRStationsInfo.as_view('nerr_sites_metadata'), methods=['GET'])

        app.add_url_rule('/resttest/cdmorestdata/login',
                         view_func=Login.as_view('cdmo_user_login'))

        app.add_url_rule('/resttest/cdmorestdata/updatealerts',
                         view_func=NERRUpdateAlerts.as_view('alerts_update'))

        app.add_url_rule('/resttest/cdmorestdata/togglealerts',
                         view_func=NERRToggleAlerts.as_view('alerts_disable'))

        app.add_url_rule('/resttest/cdmorestdata/deletealerts',
                         view_func=NERRDeleteAlerts.as_view('alerts_delete'), methods=['POST'])

    else:
        app.add_url_rule('/resttest/cdmoapi/help', view_func=CMDOAPIHelp.as_view('help'))

        app.add_url_rule('/cdmorestdata/<string:station>/data',
                         view_func=StationInfoAPI.as_view('station_info_api'), methods=['GET'])

        app.add_url_rule('/cdmorestdata/<string:reserve>/stations',
                         view_func=NERRReserveStations.as_view('nerr_reserve_stations'), methods=['GET'])

        app.add_url_rule('/cdmorestdata/<string:station>/hadsdata',
                         view_func=HADSLatestAPI.as_view('hads_data_api'), methods=['GET'])

        app.add_url_rule('/cdmorestdata/reserves',
                         view_func=NERRSitesAPI.as_view('nerr_sites_api'), methods=['GET'])

        app.add_url_rule('/cdmorestdata/stationsmetadata',
                         view_func=NERRStationsInfo.as_view('nerr_sites_metadata'), methods=['GET'])

        app.add_url_rule('/cdmorestdata/login',
                         view_func=Login.as_view('cdmo_user_login'))

        app.add_url_rule('/cdmorestdata/updatealerts',
                         view_func=NERRUpdateAlerts.as_view('alerts_update'))

        app.add_url_rule('/cdmorestdata/togglealerts',
                         view_func=NERRToggleAlerts.as_view('alerts_disable'))

        app.add_url_rule('/cdmorestdata/deletealerts',
                         view_func=NERRDeleteAlerts.as_view('delete_alert'), methods=['POST'])

    @app.errorhandler(500)
    def internal_error(exception):
        app.logger.exception(exception)

    @app.errorhandler(404)
    def internal_error(exception):
        app.logger.exception(exception)

    app.logger.debug("build_url_rules finished")


def shutdown_all():
    rts_db.disconnect()
    cdmo_db.disconnect()


def load_secret_key(app):
    current_time = datetime.now()
    #CHeck and see if we have a secret key file, if so we use that, otherwise the default from config.py.
    secret_key = SECRET_API_KEY
    key_file_path = os.path.join(app.root_path, SECRET_KEY_FILE)
    if os.path.isfile(key_file_path):
        app.logger.debug(f"Secret Key File: {key_file_path} found.")
        rotate_key = False
        with open(key_file_path, "r") as key_file_obj:
            json_key_data = json.load(key_file_obj)
            #Check the last rotated time, if we've exceeded it, we'll regen a new key.
            try:
                key_rotated_time = datetime.strptime(json_key_data['last_rotated'], "%Y-%m-%d %H:%M:%S")
                app.logger.debug(f"Key rotated time: {key_rotated_time}.")
                if current_time - key_rotated_time >= timedelta(hours=SECRET_KEY_ROTATE_HOURS):
                    app.logger.debug(f"Key time {key_rotated_time} expired, rotating.")
                    new_key = secrets.token_hex(32)
                    json_key_data['secret_key'] = new_key
                    json_key_data['last_rotated'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    rotate_key = True
            except Exception as e:
                app.logger.exception(e)
        if rotate_key:
            try:
                with open(key_file_path, "w") as key_file_obj:
                    app.logger.debug(f"Saving secret key file: {key_file_path}.")
                    json.dump(json_key_data, key_file_obj)
            except Exception as e:
                app.logger.exception(e)
        secret_key = json_key_data['secret_key']

    app.secret_key = secret_key
    return secret_key

def create_app():
    flask_app = Flask(__name__)
    # Enable Cross origin
    if not PRODUCTION_MACHINE:
        cors = CORS(flask_app, resources={r"/cdmorestdata/login": {"origins": "*"},
                                          r"/cdmorestdata/updatealerts": {"origins": "*"},
                                          r"/cdmorestdata/togglealerts": {"origins": "*"},
                                          r"/cdmorestdata/deletealerts": {"origins": "*"}})
    else:
        cors = CORS(flask_app, resources={r"/resttest/cdmorestdata/login": {"origins": "*"},
                                          r"/resttest/cdmorestdata/updatealerts": {"origins": "*"},
                                          r"/resttest/cdmorestdata/togglealerts": {"origins": "*"},
                                          r"/resttest/cdmorestdata/deletealerts": {"origins": "*"}})
    init_logging(flask_app)
    load_secret_key(flask_app)
    rts_db.connectDB(RTS_SQL_SERVER_CONN, flask_app.logger)
    cdmo_db.connectDB(CDMO_SQL_SERVER_CONN, flask_app.logger)

    build_url_rules(flask_app)
    atexit.register(shutdown_all)
    killer = GracefulKiller(rts_db, cdmo_db)
    return flask_app


app = create_app()


def get_rts_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'rts_session'):
        g.rts_session = True
    current_app.logger.debug("Returning RTS Session.")
    return rts_db.Session()


def get_cdmo_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'cdmo_session'):
        g.cdmo_session = True
    current_app.logger.debug("Returning CDMO Session.")
    return cdmo_db.Session()


@app.teardown_appcontext
def remove_session(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'rts_session'):
        rts_db.remove_session()
        current_app.logger.debug("Removing RTS Session.")
    if hasattr(g, 'cdmo_session'):
        cdmo_db.remove_session()
        current_app.logger.debug("Removing CDMO Session.")


'''
def database_connect(conn_string):
    db_obj = cdmo_sqlalchemy()
    db_obj.connectDB(conn_string, printSQL=True)
    return db_obj

def get_rts_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'rts_db'):
        g.rts_db = database_connect(RTS_SQL_SERVER_CONN)
    return g.rts_db
def get_cdmo_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'cdmo_db'):
        g.cdmo_db = database_connect(CDMO_SQL_SERVER_CONN)
    return g.cdmo_db

@app.teardown_appcontext
def remove_session(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'rts_session'):
        g.rts_session.remove_session()
    if hasattr(g, 'cdmo_session'):
        g.rts_session.remove_session()
'''

'''
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'rts_db'):
        g.rts_db.remove_session()
        #g.rts_db.disconnect()
    if hasattr(g, 'cdmo_db'):
        g.cdmo_db.remove_session()
        #g.cdmo_db.disconnect()
'''


@app.route('/resttest/hello')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
    init_logging(app)
    app.logger.debug("Run started.")
