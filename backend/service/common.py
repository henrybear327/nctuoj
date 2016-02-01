from service.base import BaseService
import config
### need to add rs

class CommonService(BaseService):
    def __init__(self, db, rs):
        super().__init__(db, rs)
        CommonService.inst = self

    def get_execute_type(self):
        res ={ x['id']: x for x in (yield self.db.execute("SELECT * FROM execute_types order by id"))}
        return res

    def get_verdict_type(self):
        res = { x['id']: x for x in (yield self.db.execute("SELECT * FROM map_verdict_string order by id"))}
        return res
