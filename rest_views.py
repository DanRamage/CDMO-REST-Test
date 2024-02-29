from flask import request, render_template, current_app, session, Response, jsonify
from flask.views import View, MethodView
from sqlalchemy import desc, inspect, select, Table
from sqlalchemy.orm import load_only
from sqlalchemy import or_
#from sqlakeyset import get_page
import uuid
import json
import time
# from requests import Request, Session
import requests
from datetime import datetime, timedelta
import pytz
from dateutil.parser import parser

from cdmo_db import get_class_by_tablename

from config import CELL_CARRIER_EMAIL_HOSTS

session_data = {}

'''
from cdmo_database import met_station_table_factory, \
    wq_station_table_factory, \
    Sampling_Station, \
    get_class_by_tablename, \
    signalStrength, \
    batteryVoltage
'''


def get_table(stationname):
    from models.cdmo_rts_models import met_station_table_factory, wq_station_table_factory

    table_obj = get_class_by_tablename(stationname)
    if table_obj is None:
        if stationname.rfind('met') != -1:
            table_obj = met_station_table_factory(stationname)
        elif stationname.rfind('wq') != -1:
            table_obj = wq_station_table_factory(stationname)
        elif stationname.rfind('nut') != -1:
            table_obj = None

    return table_obj
class CMDOAPIHelp(View):
    def dispatch_request(self):
        current_app.logger.debug('IP: %s CMDOAPIHelp rendered' % (request.remote_addr))
        return render_template("api_help.html")

class ResponseError(Exception):
    def __init__(self, arg1):
        self.status = None
        self.source = None
        self.title = None
        self.detail = None
        super(ResponseError, self).__init__(arg1)

    def as_dict(self):
        return {
            "status": self.status,
            "source": {"pointer": self.source},
            "title": self.title,
            "detail": self.detail
        }

class APIError(Exception):
    def __init__(self, arg1, status):
        super(ResponseError, self).__init__(arg1)
        self._status = status
    def as_dict(self):
        return {
            "status": self._status
        }

'''
Below are the API views.
'''


class BaseStationInfoAPI(MethodView):
    '''
    This is the parent class for the APIs. We have a few functions that are used over and over.
    '''

    def get(self, station=None):
        '''
        This is the GET reponse processing for the REST request.
        :param station:
        :return:
        '''
        start_time = time.time()
        current_app.logger.debug('IP: %s %s started' % (request.remote_addr, self.__class__.__name__))
        ret_code = 404
        results = {}
        try:
            begin_date = self.check_date_time('begin_date', request)
            end_date = self.check_date_time('end_date', request)
        except ResponseError as e:
            results = json.dumps(self.create_error_response(e))
            ret_code = 422
        else:
            station_nfo_rec = self.get_station_metadata(station)
            if station_nfo_rec is not None:
                current_app.logger.debug('IP: %s %s get for site: %s begin_date: %s end_date: %s' % (
                    request.remote_addr, self.__class__.__name__, station, begin_date, end_date))

                self._user_session_id = None
                if 'session_id' not in request.headers:
                    self._user_session_id = uuid.uuid4()
                #This is where we retrieve whatever specific data the query warrants.
                recs = self.get_query_specific_data(station, begin_date, end_date)
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(station_nfo_rec.Longitude), float(station_nfo_rec.Latitude)]
                    },
                    "properties": []
                }
                if recs is not None:
                    for rec in recs:
                        feature['properties'].append(self.as_dict(rec))
                ret_code = 200
                results = json.dumps(feature)
            else:
                ret_code = 422
                error_obj = ResponseError("The station requested: " + station + " is invalid")
                error_obj.status = ret_code
                error_obj.source = "/<valid station>/"
                error_obj.title = "Invalid Request"
                error_obj.detail = "The station requested: " + station + " is invalid"
                results = json.dumps(self.create_error_response(error_obj))

        current_app.logger.debug('IP: %s %s finished in %f seconds' % (request.remote_addr,
                                                                       self.__class__.__name__,
                                                                                    time.time() - start_time))

        return Response(results, ret_code, headers={'Access-Control-Allow-Origin': '*'},
                        content_type='Application/JSON')

    def get_query_specific_data(self, station, begin_date, end_date):
        return None

    def check_session_id(self):
        user_session_nfo = None
        if 'session' not in request.cookies:
            session.modified = True
        else:
            user_session_nfo = session_data[session['id']]
        return user_session_nfo

    def create_session_nfo(self, session_id, session_nfo):
        session_data[session_id] = session_nfo
        session['id'] = session_id
        session.modified = True



    def get_station_metadata(self, station):
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        current_app.logger.debug("IP: %s Querying station: %s metadata" % (request.remote_addr, station))
        try:
            cdmo_db = get_cdmo_db()
            station_nfo_rec = cdmo_db.query(Sampling_Station)\
                .filter(Sampling_Station.Station_Code == station).one()
            return station_nfo_rec
        except Exception as e:
            current_app.logger.exception(e)
        return None

    def as_dict(self, record):
        ret_dict = {}
        if type(record) != dict:
            mapper = inspect(record)
            for column in mapper.attrs:
                val = column.value
                if type(val) == datetime:
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                ret_dict[column.key] = val
            return ret_dict
        #Passing in a dictionary object. We simply make sure we convert any data types that can't be JSONized into a format that can.
        else:

            for column in record:
                val = record[column]
                if type(val) == datetime:
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                record[column] = val
            return record

    def check_date_time(self, date_parameter, request):
        if date_parameter in request.args:
            try:
                #date_time = datetime.strptime(request.args[date_parameter], "%Y-%m-%d %H:%M:%S")
                p = parser()
                date_time = p.parse(request.args[date_parameter])

                return date_time
            except Exception as e:
                try:
                    date_time = datetime.strptime(request.args[date_parameter], "%Y-%m-%dT%H:%M:%S%z")

                except Exception as e:
                    error = ResponseError("Incorrect " + date_parameter + " in request. Should be: "+ date_parameter + "=yyyy-mm-dd hh:mm:ss")
                    error.status = 422
                    error.title = "Invalid Request"
                    error.detail = "Incorrect " + date_parameter + " in request. Should be: "+ date_parameter + "=yyyy-mm-dd hh:mm:ss"
                    error.source = "/station?" + date_parameter + "=yyyy-mm-dd hh:mm:ss"
                    raise error
        else:
            error = ResponseError("Missing " + date_parameter + " in request. Should be: " + date_parameter + "=yyyy-mm-dd hh:mm:ss")
            error.status = 422
            error.title = "Invalid Request"
            error.detail = "Missing " + date_parameter + " in request. Should be: " + date_parameter + "=yyyy-mm-dd hh:mm:ss"
            error.source = "/station?" + date_parameter + "=yyyy-mm-dd hh:mm:ss"
            raise error

        return None
    def create_error_response(self, errors):
        error_json = {
            "errors": [
            ]
        }
        if type(errors) == list:
            for error in errors:
                error_json["errors"].append(error.as_dict())
        else:
            error_json["errors"].append(errors.as_dict())

        return error_json

    def get_model_class(self, query):
        classes = []
        for t in query.selectable.froms:
        #for t in query.selectable.locate_all_froms():
            if type(t) == Table:
                classes.append(get_class_by_tablename(t.name))
            else:
                classes.append(get_class_by_tablename(t.froms[0]))
        return classes
    def filter_query(self, query, seperator):

        model_class = self.get_model_class(query)  # returns the query's Model
        raw_filters = request.args.getlist('filter')
        for raw in raw_filters:
            try:
                key, op, value = raw.split(seperator, 3)
            except ValueError:
                raise APIError(400, 'Invalid filter: %s' % raw)
            column = getattr(model_class[0], key, None)
            if not column:
                raise APIError(400, 'Invalid filter column: %s' % key)
            if op == 'in':
                filt = column.in_(value.split(','))
            else:
                try:
                    attr = None
                    for test_op in ['%s', '%s_', '__%s__']:
                        test_attr = test_op % op
                        if hasattr(column, test_attr):
                            attr = test_attr
                            break
                    #filt_result = filter(
                    #    lambda e: hasattr(column, e % op), ['%s', '%s_', '__%s__']
                    #)
                    #attr = list(filt_result)[0] % op
                except IndexError:
                    raise APIError(400, 'Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            query = query.filter(filt)
        return query

class NERRStationsInfo(BaseStationInfoAPI):
    def get(self):
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        try:
            db_obj = get_cdmo_db()
            recs_q = db_obj.query(Sampling_Station)
            recs_q = self.filter_query(recs_q, ';')

            features = {
                'type': 'FeatureCollection',
                'features': []
            }
            recs = recs_q.all()
            for rec in recs:
                features['features'].append({
                    'type': 'Feature',
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(rec.Longitude), float(rec.Latitude)]
                    },
                    'properties': rec.as_dict()
                })
            resp = jsonify(features)
        except Exception as e:
            current_app.logger.exception(e)
            resp = Response({}, 404, content_type='Application/JSON')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp

class NERRReserveStations(BaseStationInfoAPI):
    def get(self, reserve=None):
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station, Sampling_Station_API_Allowed_Columns
        try:
            db_obj = get_cdmo_db()
            recs_q = db_obj.query(Sampling_Station).filter(Sampling_Station.NERR_Site_ID == reserve)

            if 'RealTime' in request.args:
                real_time = None
                if int(request.args['RealTime']) == 1:
                    real_time = 'R'
                recs_q = recs_q.filter(or_(Sampling_Station.Real_Time == real_time,
                                           Sampling_Station.HADS_ID != None))

            features = {
                'type': 'FeatureCollection',
                'features': []
            }
            recs = recs_q.all()
            for rec in recs:
                features['features'].append({
                    'type': 'Feature',
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(rec.Longitude), float(rec.Latitude)]
                    },
                    'properties': rec.as_dict(column_list=Sampling_Station_API_Allowed_Columns)
                })
            resp = jsonify(features)
        except Exception as e:
            current_app.logger.exception(e)
            resp = Response({}, 404, content_type='Application/JSON')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp


def token_required(f):

    def decorator(*args, **kwargs):
        import jwt
        from app import get_cdmo_db
        from models.cdmo_db_models import CDMO_Users

        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            try:
                cdmo_db = get_cdmo_db()
                cdmo_user = cdmo_db.query(CDMO_Users) \
                    .filter(CDMO_Users.User_name == data['sub']) \
                    .first()

            except Exception as e:
                current_app.logger.exception(e)
                cdmo_user = None

            #user = User.query.filter_by(email=data['sub']).first()
            if not cdmo_user:
                raise RuntimeError('User not found')
            return f(cdmo_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return decorator

'''
class NERRAlerts(BaseStationInfoAPI):
    decorators = [token_required]
    def get(self):
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        try:
            db_obj = get_cdmo_db()
            recs_q = db_obj.query(Sampling_Station)
            recs_q = self.filter_query(recs_q, ';')

            features = {
                'type': 'FeatureCollection',
                'features': []
            }
            recs = recs_q.all()
            for rec in recs:
                features['features'].append({
                    'type': 'Feature',
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(rec.Longitude), float(rec.Latitude)]
                    },
                    'properties': rec.as_dict()
                })
            resp = jsonify(features)
        except Exception as e:
            current_app.logger.exception(e)
            resp = Response({}, 404, content_type='Application/JSON')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
'''

class NERRUpdateAlerts(BaseStationInfoAPI):
    decorators = [token_required]
    def post(self, cdmo_user):
        start_time = time.time()
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        try:
            ret_code = 400
            current_app.logger.debug("IP: %s NERRUpdateAlerts POST started. ARGS: %s" % (request.remote_addr, request.args))
            db_obj = get_cdmo_db()
            #Select the station first.
            station_update = db_obj.query(Sampling_Station) \
                .filter(Sampling_Station.Station_Code == request.args['station']) \
                .first()

            args = request.args
            station_update.activeAlerts = 'yes'
            try:
                if len(args['battery_voltage']) and station_update.alertValue != float(args['battery_voltage']):
                    station_update.alertValue = float(args['battery_voltage'])
            except ValueError as e:
                current_app.logger.exception(e)
            if (len(args['text_alert_number']) and station_update.alertNumber != args['text_alert_number']):
                #We need the number and the cell provider to create the email address.
                if len(args['cellular_carrier']):
                    if args['cellular_carrier'] in CELL_CARRIER_EMAIL_HOSTS:
                        station_update.alertNumber = '%s@%s' % (args['text_alert_number'],  CELL_CARRIER_EMAIL_HOSTS[args['cellular_carrier']])
            if len(args['alert_email_primary']) and station_update.alertEmail != args['alert_email_primary']:
                station_update.alertEmail = args['alert_email_primary']
            if len(args['alert_email_secondary']) and station_update.alertEmailOther != args['alert_email_secondary']:
                station_update.alertEmailOther = args['alert_email_secondary']
            if len(args['param_1']) and station_update.alertParam1 != args['param_1']:
                station_update.alertParam1 = args['param_1']
            try:
                if len(args['param_1_min']) and station_update.alertValueMin1 != float(args['param_1_min']):
                    station_update.alertValueMin1 = float(args['param_1_min'])
            except ValueError as e:
                current_app.logger.exception(e)
            try:
                if len(args['param_1_max']) and station_update.alertValueMax1 != float(args['param_1_max']):
                    station_update.alertValueMax1 = float(args['param_1_max'])
            except ValueError as e:
                current_app.logger.exception(e)
            if len(args['param_2']) and station_update.alertParam2 != args['param_2']:
                station_update.alertParam2 = args['param_2']
            try:
                if len(args['param_2_min']) and station_update.alertValueMin2 != float(args['param_2_min']):
                    station_update.alertValueMin2 = float(args['param_2_min'])
            except ValueError as e:
                current_app.logger.exception(e)
            try:
                if len(args['param_2_max']) and station_update.alertValueMax2 != float(args['param_2_max']):
                    station_update.alertValueMax2 = float(args['param_2_max'])
            except ValueError as e:
                current_app.logger.exception(e)
            if len(args['param_3']) and station_update.alertParam3 != args['param_3']:
                station_update.alertParam3 = args['param_3']
            try:
                if len(args['param_3_min']) and station_update.alertValueMin3 != float(args['param_3_min']):
                    station_update.alertValueMin3 = float(args['param_3_min'])
            except ValueError as e:
                current_app.logger.exception(e)
            try:
                if len(args['param_3_max']) and station_update.alertValueMax3 != float(args['param_3_max']):
                    station_update.alertValueMax3 = float(args['param_3_max'])
            except ValueError as e:
                current_app.logger.exception(e)
            resp = {
                'message': 'Alerts update successful'
            }
            ret_code = 200
            db_obj.commit()
        except Exception as e:
            current_app.logger.exception(e)
            resp = {
                'message': 'Failed to update the alerts'
            }
            ret_code = 401


        current_app.logger.debug("IP: %s NERRUpdateAlerts POST finished in %f seconds" % (request.remote_addr, time.time()-start_time))

        return jsonify(resp), ret_code

class NERRToggleAlerts(BaseStationInfoAPI):
    '''
    This handler is for enabling/disabling the alerts in the Sampling_Station table. This table has 3 alert columns(
    not a relational table) along with the metadata for the station. We just toggle the activeAlerts field to 'yes' or 'no'.
    '''

    decorators = [token_required]
    def post(self, cdmo_user):
        start_time = time.time()
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        try:
            ret_code = 400
            current_app.logger.debug("IP: %s NERRDisableAlerts POST started. ARGS: %s" % (request.remote_addr, request.args))
            args = request.args
            if 'alerts_state' in args:
                db_obj = get_cdmo_db()
                #Select the station first.
                station_update = db_obj.query(Sampling_Station) \
                    .filter(Sampling_Station.Station_Code == request.args['station']) \
                    .first()
                #station_update.activeAlerts = 'no'
                if len(args['alerts_state']) and station_update.activeAlerts != bool(args['alerts_state']):
                    if int(args['alerts_state']):
                        station_update.activeAlerts = 'yes'
                    else:
                        station_update.activeAlerts = 'no'
                    current_app.logger.debug(
                        "IP: %s NERRDisableAlerts alert active set to: %s" % (request.remote_addr, station_update.activeAlerts))

                '''
                station_update.alertValue = None
                station_update.alertNumber = None
                station_update.alertEmail = None
                station_update.alertEmailOther = None
                station_update.alertParam1 = None
                station_update.alertValueMin1 = None
                station_update.alertValueMax1 = None
                station_update.alertParam2 = None
                station_update.alertValueMin2 = None
                station_update.alertValueMax2 = None
                station_update.alertParam3 = None
                station_update.alertValueMin3 = None
                station_update.alertValueMax3 = None
                '''
                resp = {
                    'message': 'Alerts disable successful'
                }
                ret_code = 200
                db_obj.commit()
            else:
                resp = {
                    'message': 'Failed to disable the alerts'
                }
                ret_code = 401

        except Exception as e:
            current_app.logger.exception(e)
            resp = {
                'message': 'Failed to disable the alerts'
            }
            ret_code = 401


        current_app.logger.debug("IP: %s NERRDisableAlerts POST finished in %f seconds" % (request.remote_addr, time.time()-start_time))

        return jsonify(resp), ret_code

class NERRSitesAPI(MethodView):
    def get(self):
        from app import get_cdmo_db
        from models.cdmo_db_models import NERR_Sites
        start_time = time.time()
        try:
            cdmo_db = get_cdmo_db()
            nerr_recs = cdmo_db.query(NERR_Sites)\
                .order_by(NERR_Sites.NERR_Site_Code).all()
            features = {
                'type': 'FeatureCollection',
                'features': []
            }

            for rec in nerr_recs:
                features['features'].append({
                    'type': 'Feature',
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(rec.reserveLongitude), float(rec.reserveLatitude)]
                    },
                    'properties': rec.as_dict()
                })
            resp = jsonify(features)
        except Exception as e:
            current_app.logger.exception(e)
            resp = Response({}, 404, content_type='Application/JSON')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        current_app.logger.debug("IP: %s NERRSitesAPI finished in %f seconds." % (request.remote_addr, time.time()-start_time))
        return resp

class StationInfoAPI(BaseStationInfoAPI):

    def get_signal_strength(self, station, begin_date, end_date):
        from app import get_cdmo_db
        from models.cdmo_db_models import signalStrength
        try:
            start_time = time.time()
            db_obj = get_cdmo_db()
            recs_q = db_obj.query(signalStrength) \
                .filter(signalStrength.DateTimeStamp >= begin_date) \
                .filter(signalStrength.DateTimeStamp < end_date) \
                .filter(signalStrength.stationCode == station)\
                .order_by(signalStrength.DateTimeStamp)
            recs = recs_q.all()
            current_app.logger.debug("IP: %s Signal strength query for %s in %f seconds." % \
                                     (request.remote_addr, station, time.time()-start_time))

            return recs
        except Exception as e:
            current_app.logger.exception(e)
        return None

    def get_battery_voltage(self, station, begin_date, end_date):
        from app import get_cdmo_db
        from models.cdmo_db_models import batteryVoltage, StationBatteryVoltage
        try:
            start_time = time.time()
            db_obj = get_cdmo_db()
            if station.lower().find('wq') == -1:
                recs = db_obj.query(batteryVoltage) \
                    .filter(batteryVoltage.DateTimeStamp >= begin_date) \
                    .filter(batteryVoltage.DateTimeStamp < end_date) \
                    .filter(batteryVoltage.samplingStation == station) \
                    .order_by(batteryVoltage.DateTimeStamp).all()
                    #.order_by(desc('DateTimeStamp')).all()
            else:
                qry = db_obj.query(StationBatteryVoltage) \
                    .filter(StationBatteryVoltage.DateTimeStamp >= begin_date) \
                    .filter(StationBatteryVoltage.DateTimeStamp < end_date) \
                    .filter(StationBatteryVoltage.samplingStation == station) \
                    .order_by(StationBatteryVoltage.DateTimeStamp)
                recs = qry.all()
            current_app.logger.debug("IP: %s Battery voltage query for %s finished in %f seconds." % \
                                     (request.remote_addr, station, time.time()-start_time))
            return recs
        except Exception as e:
            current_app.logger.exception(e)
        return None

    def get_query_specific_data(self, station, begin_date, end_date):
        from app import get_rts_db

        start_time = time.time()
        ret_recs = None
        # CHeck to see if one of the filters is either signal or battery voltage.
        param_list = []
        if 'parameters' in request.args:
            param_list = request.args['parameters'].split(',')
        sig_recs = None
        batt_recs = None
        has_params = False
        if len(param_list):
            has_params = True
            if 'signalStrength' in param_list:
                sig_recs = self.get_signal_strength(station, begin_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
                # Pull filter out since it's not a column in the station tables
                param_list.remove('signalStrength')
            if 'batteryVolts' in param_list:
                batt_recs = self.get_battery_voltage(station, begin_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
                param_list.remove('batteryVolts')

        db_obj = get_rts_db()
        # gets the first page
        db_table = get_table(station)
        try:
            if len(param_list) or has_params:
                param_list.append('DateTimeStamp')
                recs_q = db_obj.query(*[getattr(db_table, attr) for attr in param_list])
            # User is requesting all parameters from station.
            else:
                recs_q = db_obj.query(db_table)
            #user_session_nfo = self.check_session_id()
            if 'page' not in request.args:
                recs_q = recs_q.filter(db_table.DateTimeStamp >= begin_date.strftime("%Y-%m-%d %H:%M:%S"))
                recs_q = recs_q.filter(db_table.DateTimeStamp < end_date.strftime("%Y-%m-%d %H:%M:%S"))
                recs_q = self.filter_query(recs_q, ';')
                recs_q = recs_q.order_by(db_table.DateTimeStamp)

                #self.create_session_nfo(self._user_session_id, {'query_object': recs_q})
                #If we queried based on parameters, we need to build the record list we return. We have to merge in the
                #battery and signal with the measurements.
                rec_list = []
                if len(param_list):
                    recs = recs_q.all()
                    if len(recs):
                        for rec in recs:
                            rec_row = {}
                            for ndx, param in enumerate(rec):
                                rec_row[param_list[ndx]] = param
                            rec_list.append(rec_row)

                if sig_recs is not None or batt_recs is not None:
                    if len(rec_list):
                        rec_dates_list = [rec['DateTimeStamp'] for rec in rec_list]
                    else:
                    #This can happen if we're not saving the stations results to the database. Usually when
                    #a station is coming online and we're debugging it.
                        if len(sig_recs):
                            rec_dates_list = [rec.DateTimeStamp for rec in sig_recs]
                        elif len(batt_recs):
                            rec_dates_list = [rec.DateTimeStamp for rec in batt_recs]

                if sig_recs is not None:
                        append_list = []
                        sig_dates_list = [sig_rec.DateTimeStamp for sig_rec in sig_recs]
                        #Build sets() for the datetimes for the signal, battery and datarecords so it's quicker to merge.
                        #sig_dates_set = set()
                        #rec_dates_set = set(rec['DateTimeStamp'] for rec in rec_list)
                        #merged_set = rec_dates_set.union(sig_dates_set)
                        for ndx,date_rec in enumerate(sig_dates_list):
                            sig_rec = sig_recs[ndx]
                            if len(rec_list):
                                try:
                                    rec_ndx = rec_dates_list.index(date_rec)
                                    rec_list[rec_ndx]['signalStrength'] = sig_rec.signalStrength
                                except ValueError as e:
                                    append_list.append({'DateTimeStamp': sig_rec.DateTimeStamp,
                                                     'signalStrength': sig_rec.signalStrength})

                            else:
                                append_list.append({'DateTimeStamp': sig_rec.DateTimeStamp,
                                                    'signalStrength': sig_rec.signalStrength})

                        if len(append_list):
                            rec_list.extend(append_list)
                if batt_recs is not None:
                    append_list = []
                    batt_dates_list = [batt_rec.DateTimeStamp for batt_rec in batt_recs]
                    for ndx,date_rec in enumerate(batt_dates_list):
                        batt_rec = batt_recs[ndx]
                        if len(rec_list):
                            try:
                                rec_ndx = rec_dates_list.index(date_rec)
                                rec_list[rec_ndx]['batteryVolts'] = batt_rec.batteryVolts
                            except ValueError as e:
                                append_list.append({'DateTimeStamp': batt_rec.DateTimeStamp,
                                                 'batteryVolts': batt_rec.batteryVolts})

                        else:
                            append_list.append({'DateTimeStamp': batt_rec.DateTimeStamp,
                                             'batteryVolts': batt_rec.batteryVolts})

                    if len(append_list):
                        rec_list.extend(append_list)

                if len(rec_list):
                    #Now let's sort the return based on DateTimeStamp
                    rec_list.sort(key=lambda rec: rec['DateTimeStamp'])
                    ret_recs = rec_list
                else:
                    ret_recs = recs_q.all()
            '''
            else:                    
                if user_session_nfo is not None:
                    db_obj = get_rts_db()
                    db_table = get_table(station)
                    recs_q = db_obj.query(db_table) \
                        .filter(db_table.DateTimeStamp >= begin_date) \
                        .filter(db_table.DateTimeStamp < end_date) \
                        .order_by(db_table.DateTimeStamp)
                    next_page = get_page(recs_q, per_page=10, page=user_session_nfo['next_page'])
                    self.create_session_nfo(self._user_session_id,
                                            {'query_object': user_session_nfo['query_object'], 'next_page': next_page.paging.next})
                    return next_page
                            
            '''
        except Exception as e:
            current_app.logger.exception(e)
        current_app.logger.debug("get_query_specific_data for %s finished in %f seconds." % (station, time.time()-start_time))
        return ret_recs
'''
class SignalStrengthAPI(BaseStationInfoAPI):
    def get_query_specific_data(self, station, begin_date, end_date):
        from app import get_cdmo_db
        from models.cdmo_db_model import signalStrength
        try:
            db_obj = get_cdmo_db()
            recs_q = db_obj.query(signalStrength) \
                .filter(signalStrength.stationCode == station)\
                .filter(signalStrength.DateTimeStamp >= begin_date) \
                .filter(signalStrength.DateTimeStamp < end_date) \
                .order_by(signalStrength.DateTimeStamp)

            page1 = get_page(recs_q, per_page=10)

            return page1
        except Exception as e:
            current_app.logger.exception(e)
        return None

class BatteryVoltageAPI(BaseStationInfoAPI):
    def get_query_specific_data(self, station, begin_date, end_date):
        from app import get_cdmo_db
        from models.cdmo_db_models import batteryVoltage
        try:
            db_obj = get_cdmo_db()
            recs = db_obj.query(batteryVoltage) \
                .filter(batteryVoltage.samplingStation == station) \
                .filter(batteryVoltage.DateTimeStamp >= begin_date) \
                .filter(batteryVoltage.DateTimeStamp < end_date) \
                .order_by(desc('DateTimeStamp')).all()
            return recs
        except Exception as e:
            current_app.logger.exception(e)
        return None
'''
hads_to_cdmo_observation_mapping = {
    #WQ Params
    "TW": "Temp",
    "WC": "SpCond",
    "WS": "Sal",
    "WO": "DO_mgl",
    'WX': "DO_pct",
    "HM": "Depth",
    "WP": "pH",
    "WT": "Turb",
    "WF": "ChlFluor",
    "VB": "AvgVolt",
    #Met Params
    "TA": "ATemp",
    "VJA": "MaxTemp",
    "DJA": "MaxTempT",
    "VJB": "MinTemp",
    "DJB": "MinTempT",
    "XR": "RH",
    "PA": "BP",
    "US": "WSpd",
    "UD": "Wdir",
    "UE": "SDWDir",
    "VUP": "MaxWSpd",
    "DUP": "MaxWSpT",
    "PP": "TotPrcp",
    "RS": "TotPAR"
}
class HADSLatestAPI(MethodView):
    def get_station_metadata(self, station):
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station

        try:
            cdmo_db = get_cdmo_db()
            station_nfo_rec = cdmo_db.query(Sampling_Station)\
                .filter(Sampling_Station.Station_Code == station).one()
            return station_nfo_rec
        except Exception as e:
            current_app.logger.exception(e)
        return None
    def process_hads_row(self, row, parser_obj, station_nfo_rec):
        try:
            fields = row.split("|")[0:-1]
            if fields[2] in hads_to_cdmo_observation_mapping:
                cdmo_obs = hads_to_cdmo_observation_mapping[fields[2]]
            else:
                cdmo_obs = fields[2]
            # WE get the HADS data in UTC, so we convert to the Reserves timezone by using the GMT offset.
            dt = parser_obj.parse(fields[3]).replace(tzinfo=pytz.utc) + timedelta(hours=int(station_nfo_rec.GMT_Offset.strip()))
            try:
                value = float(fields[4])
            except ValueError:
                value = None
            date_time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            return({
                'date': date_time_str,
                'cdmo_obs': cdmo_obs,
                'value': value
            })
        except Exception as e:
            current_app.logger.exception(e)
        return None

    def get(self, station=None):
        start_time = time.time()
        self._base_url = "https://hads.ncep.noaa.gov/nexhads2/servlet/DecodedData"
        ret_code = 404
        results = {}
        utc_tz = pytz.timezone('UTC')
        #rvar = re.compile("""\n\s([A-Z]{2}[A-Z0-9]{0,1})\(\w+\)""")
        #If we want just the last update, within in the 7 days
        get_last_update = False
        if 'last_update' in request.args:
            if request.args['last_update']:
                get_last_update = True


        current_app.logger.debug('IP: %s HADSLatestAPI get for site: %s' % (request.remote_addr, station))
        station_nfo_rec = self.get_station_metadata(station)
        '''
        For an of=1, this is the format of the data:
        3B031302|NIQS1|TW|2019-02-06 16:30|55.67|  |
        3B031302|NIQS1|TW|2019-02-06 16:45|56.50|  |
        3B031302|NIQS1|TW|2019-02-06 17:00|57.13|  |
        3B031302|NIQS1|WC|2019-02-06 16:30|46170.00|  |        
        '''
        if station_nfo_rec is not None:
            data = {
            'state' : 'nil',
            'hsa': 'nil',
            'of': '1',
            #'extraids': station_nfo_rec.HADS_ID.strip(),
            'nesdis_ids': station_nfo_rec.HADS_ID.strip(),
            'data': 'Decoded+Data'
            }
            if get_last_update:
                data['sinceday'] = 1
            else:
                data['sinceday'] = 7
            p = parser()
            hads_data = {}
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(station_nfo_rec.Longitude), float(station_nfo_rec.Latitude)]
                },
                "properties": []
            }
            #url_data = ''
            #for k,v in data.items():
            #    url_data += "%s=%s&" % (k,v)

            try:
                resp = requests.post(self._base_url, data=data)
                #current_app.logger.debug("IP: %s HADSLatestAPI get for site: %s url: %s" %
                #                         (request.remote_addr, station,full_url))
                if resp.status_code == 200:
                    if len(resp.text):
                        data_rows = resp.text.splitlines()

                        for line in data_rows:
                            try:
                                #current_app.logger.debug('IP: %s HADSLatestAPI get for site: %s response: %s' % (
                                #request.remote_addr, station, line))
                                if len(line) == 0:
                                    continue

                                fields = line.split("|")[0:-1]
                                if fields[2] in hads_to_cdmo_observation_mapping:
                                    cdmo_obs = hads_to_cdmo_observation_mapping[fields[2]]
                                else:
                                    cdmo_obs = fields[2]
                                # WE get the HADS data in UTC, so we convert to the Reserves timezone by using the GMT offset.
                                dt = p.parse(fields[3]).replace(tzinfo=pytz.utc) + timedelta(
                                    hours=int(station_nfo_rec.GMT_Offset.strip()))
                                try:
                                    value = float(fields[4])
                                except ValueError:
                                    value = None
                                date_time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                                if date_time_str not in hads_data:
                                    hads_data[date_time_str] = []
                                cur_rec = hads_data[date_time_str]
                                cur_rec.append((cdmo_obs, value))
                            except Exception as e:
                                current_app.logger.exception(e)
                        #Now let's build a single record per time.
                        time_keys = sorted(hads_data.keys())
                        single_recs = []
                        #If we are just getting latest, pull most current time to build record.
                        if get_last_update:
                            rec_time = time_keys[-1]
                            time_slot = {'DateTimeStamp': rec_time}
                            single_recs.append(time_slot)
                            for obs in hads_data[rec_time]:
                                time_slot[obs[0]] = obs[1]
                        else:
                            for rec_time in time_keys:
                                time_slot = {'DateTimeStamp': rec_time}
                                for obs in hads_data[rec_time]:
                                    time_slot[obs[0]] = obs[1]
                                single_recs.append(time_slot)

                        feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [float(station_nfo_rec.Longitude), float(station_nfo_rec.Latitude)]
                            },
                            "properties": single_recs
                        }
                        ret_code = 200
                    else:
                        current_app.logger.error('IP: %s HADSLatestAPI get for site: %s no data payload from query' % (
                        request.remote_addr, station))
                        ret_code = 204
                else:
                    current_app.logger.error('IP: %s HADSLatestAPI get for site: %s HTML status: %d' % (request.remote_addr, station, resp.status_code))
                    ret_code = resp.status_code
            except Exception as e:
                current_app.logger.exception(e)
            results = json.dumps(feature)

        else:
            ret_code = 422
            error_obj = ResponseError("The station requested: " + station + " is invalid")
            error_obj.status = ret_code
            error_obj.source = "/<valid station>/"
            error_obj.title = "Invalid Request"
            error_obj.detail = "The station requested: " + station + " is invalid"
            results = json.dumps(self.create_error_response(error_obj))

        current_app.logger.debug('IP: %s HADSLatestAPI get for site: %s finished in %f seconds' %
                                 (request.remote_addr, station, time.time() - start_time))
        return Response(results, ret_code, headers={'Access-Control-Allow-Origin': '*'}, content_type='Application/JSON')

    '''Login'''

class Login(MethodView):
        def authenticate(self, user_name, password):
            start_time = time.time()
            from app import get_cdmo_db
            from models.cdmo_db_models import CDMO_Users
            current_app.logger.debug("IP: %s Authenticating user" % (request.remote_addr))
            try:
                cdmo_db = get_cdmo_db()
                cdmo_user = cdmo_db.query(CDMO_Users)\
                    .filter(CDMO_Users.User_name == user_name)\
                    .filter(CDMO_Users.Password == password)\
                    .one()

            except Exception as e:
                current_app.logger.exception(e)
                cdmo_user = None

            current_app.logger.debug("IP: %s finished authenticating user in %f seconds" % \
                                     (request.remote_addr, time.time()-start_time))
            return cdmo_user

        def post(self):
            import jwt

            ret_code = 403
            try:
                current_app.logger.debug("IP: %s Login user" % (request.remote_addr))
                #data = request.get_json()
                user = request.authorization['username']
                pwd = request.authorization['password']
                cdmo_user = self.authenticate(user, pwd)
                if cdmo_user is not None:
                    token = jwt.encode({
                        'sub': cdmo_user.User_name,
                        'iat': datetime.utcnow(),
                        'exp': datetime.utcnow() + timedelta(minutes=30)},
                        current_app.config['SECRET_KEY'])
                    token_json = jsonify({'token': token,
                                          'cdmo_access': cdmo_user.CDMO_Access,
                                          'reserve': cdmo_user.Reserve_Only})
                    return token_json
                else:
                    token_json = jsonify({'message': 'Invalid credentials', 'authenticated': False}), 401

            except Exception as e:
                current_app.logger.exception(e)
            return token_json


class NERRDeleteAlerts(BaseStationInfoAPI):
    '''
    This handler is for deleting(blanking out) the alerts in the Sampling_Station table. This table has 3 alert columns(
    not a relational table) along with the metadata for the station. So to delete we just None out the values.
    '''
    decorators = [token_required]
    def post(self, cdmo_user):
        start_time = time.time()
        from app import get_cdmo_db
        from models.cdmo_db_models import Sampling_Station
        try:
            ret_code = 400
            current_app.logger.debug("IP: %s NERRDeleteAlerts POST started. ARGS: %s" % (request.remote_addr, request.args))
            db_obj = get_cdmo_db()
            #Select the station first.
            station_update = db_obj.query(Sampling_Station) \
                .filter(Sampling_Station.Station_Code == request.args['station']) \
                .first()
            station_update.activeAlerts = ''
            station_update.alertValue = None
            station_update.alertNumber = None
            station_update.alertEmail = None
            station_update.alertEmailOther = None
            station_update.alertParam1 = None
            station_update.alertValueMin1 = None
            station_update.alertValueMax1 = None
            station_update.alertParam2 = None
            station_update.alertValueMin2 = None
            station_update.alertValueMax2 = None
            station_update.alertParam3 = None
            station_update.alertValueMin3 = None
            station_update.alertValueMax3 = None

            resp = {
                'message': 'Alerts delete successful'
            }
            ret_code = 200
            db_obj.commit()
        except Exception as e:
            current_app.logger.exception(e)
            resp = {
                'message': 'Failed to delete the alerts'
            }
            ret_code = 401


        current_app.logger.debug("IP: %s NERRDeleteAlerts POST finished in %f seconds" % (request.remote_addr, time.time()-start_time))

        return jsonify(resp), ret_code

