from req import RequestHandler
from req import reqenv
from req import Service


class ApiExecutesHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        pass

    @reqenv
    def delete(self):
        pass

class ApiExecuteHandler(RequestHandler):
    @reqenv
    def get(self, id):
        pass

    @reqenv
    def post(self, id):
        args = ["description", "lang"]
        meta = self.get_args(args)
        meta["setter_user_id"] = self.account['id']
        meta['id'] = id
        if self.map_power['execute_manage'] not in self.account['power']:
            self.error("Permission Denied")
            return
        err, data = yield from Service.Execute.post_bulletin(meta)
        if err: self.error(err)
        else: self.success({"id": data})

    @reqenv
    def delete(self, id):
        pass