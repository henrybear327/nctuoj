from service.base import BaseService
import config

class ExecuteService(BaseService):
    def __init__(self, db, rs):
        super().__init__(db, rs)

        ExecuteService.inst = self

    def get_execute_list(self, data={}):
        sql = "SELECT e.*, u.account as setter_user  FROM execute_types as e, users as u WHERE e.setter_user_id=u.id"
        res = yield from self.db.execute(sql)
        return (None, res)

    
    def get_execute(self, data={}):
        required_args = ['id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        if int(data['id']) == 0:
            col = ("id", "description", "lang")
            res = {}
            for x in col:
                res[x] = ""
            res['steps'] = []
            res['id'] = 0
            return (None, res)
        sql = "SELECT e.*, u.account as setter_user  FROM execute_types as e, users as u WHERE e.id=%s AND e.setter_user_id=u.id"
        res = yield from self.db.execute(sql, (data["id"]))
        if len(res) == 0:
            return ('Error execute id', None)
        res = res[0]
        res['steps'] = yield from self.db.execute("SELECT execute_steps.* FROM execute_steps WHERE execute_type_id=%s", (res['id'],))
        return (None, res)

    def post_execute(self, data={}):
        required_args = ['id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        if int(data['id']) == 0:
            data.pop('id')
            sql, parma = self.gen_insert_sql("execute_types", data)
            insert_id = yield from self.db.execute(sql, parma)
            return (None, insert_id)
        else:
            id = data['id']
            data.pop('id')
            sql, parma = self.gen_update_sql("execute_types", data)
            yield from self.db.execute("%s WHERE id = %s" % (sql, str(id)), parma)
            return (None, str(id))

