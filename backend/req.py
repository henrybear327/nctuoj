import json
import logging
import msgpack
import types
import datetime
import collections
import tornado.template
import tornado.gen
import tornado.web
import tornado.websocket
from power import map_power, map_group_power class Service:
    pass

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        try:
            self.get_argument('json')
            self.res_json = True

        except tornado.web.HTTPError:
            self.res_json = False

    def log(self, msg):
        if not self.acct:
            id = 0
        else:
            id = self.acct['id']
        msg = '<USER %d> '%id + str(msg)
        logging.debug(msg)

    def error(self, err):
        self.finish(json.dumps({'status': 'error',
                                'msg': err}))
        return

    def success(self, msg):
        self.finish(json.dumps({'status': 'success',
                                'msg': msg}))
        return

    def set_secure_cookie(self, name, value, expires_days=30, version=None, **kwargs):
        kwargs['httponly'] = True
        #kwargs['secure'] = True
        super().set_secure_cookie(name, value, expires_days, version, **kwargs)

    def get_args(self, name):
        meta = {}
        for n in name:
            meta[n] = self.get_argument(n, None)
        return meta

    def get_file(self, name):
        try:
            return self.request.files[name][0]
        except:
            return None

    def render(self, templ, **kwargs):
        kwargs['map_power'] = self.map_power
        kwargs['map_group_power'] = self.map_group_power
        kwargs['account'] = self.account
        kwargs['title'] = kwargs["title"] + " | NCTUOJ" if "title" in kwargs else "NCTUOJ"
        kwargs['group'] = self.group
        try:
            kwargs['current_group'] = self.current_group
        except:
            kwargs['current_group'] = 1
        print("This function in req.py's render: ", kwargs)
        class _encoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat()

                else:
                    return json.JSONEncoder.default(self,obj)

        def _mp_encoder(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return obj

        if self.res_json == True:
            self.finish(json.dumps(kwargs, cls=_encoder))

        else:
            tpldr = tornado.template.Loader('./web/template')
            data = tpldr.load(templ).generate(**kwargs)
            self.finish(data)

        return

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def reqenv(func):
    @tornado.gen.coroutine
    def wrap(self, *args, **kwargs):
        self.map_power = map_power
        self.map_group_power = map_group_power
        self.account = {}
        self.group = {}
        try:
            id = self.get_secure_cookie('id').decode()
            err, data = yield from Service.User.get_user_basic_info(id)
            if err:
                id = None
                self.clear_cookie('id')
            else:
                self.account = data
        except:
            id = 0
            self.clear_cookie('id')
        self.account["id"] = id
        err, self.account['power'] = yield from Service.User.get_user_power_info(id)
        err, self.group = yield from Service.User.get_user_group_info(id)
        err, self.group_power = yield from Service.User.get_user_group_power_info(id)
        #self.group = group_data
        #self.account['power'] = power_data
        
        ret = func(self, *args, **kwargs)
        if isinstance(ret, types.GeneratorType):
            ret = yield from ret

        return ret

    return wrap
