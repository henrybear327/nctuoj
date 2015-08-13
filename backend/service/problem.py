from service.base import BaseService
import config

class ProblemService(BaseService):
    def __init__(self, db, rs):
        super().__init__(db, rs)
        ProblemService.inst = self

    def get_problem_list(self, data={}):
        required_args = ['group_id', 'page', 'count']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        subsql = """
            (SELECT
            p.`id` 
            FROM `problems` as p
            """
        if int(data['group_id']) == 1:
            if data['is_admin']:
                subsql += "WHERE (p.group_id=%s OR p.visible = 2)"
            else:
                subsql += "WHERE ((p.group_id=%s AND p.visible <> 0) OR p.visible = 2)"
        else:
            if data['is_admin']:
                subsql += "WHERE p.group_id=%s"
            else:
                subsql += "WHERE p.group_id=%s AND p.visible <> 0"
        subsql += "ORDER BY p.id limit %s, %s) as p2"
        sql = """
            SELECT
            p.`id`, p.`title`, p.`source`, p.`group_id`, p.`created_at`, 
            u.`id` as setter_user_id, u.`account` as setter_user,
            g.`name` as `group_name`
            FROM `problems` as p, `users` as u, `groups` as g, 
            """ + subsql + """
            WHERE u.id = p.setter_user_id AND g.id = p.group_id AND p.id = p2.id
            """
        res = yield from self.db.execute(sql, (data['group_id'], (int(data["page"])-1)*int(data["count"]), data["count"], ))
        for x in range(len(res)):
            res[x]['real_id'] = res[x]['id']
            res[x]['id'] = ((int)(data['page'])-1) * (int(data['count'])) + x + 1
        return (None, res)
        
    def get_problem_list_count(self, data={}):
        required_args = ['group_id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        res = self.rs.get('problem_list_count@%s@%s' 
                % (str(data['is_admin']), str(data['group_id'])))
        if res: return (None, res)
        sql = "SELECT COUNT(*) FROM problems as p "
        if int(data['group_id']) == 1:
            if data['is_admin']:
                sql += "WHERE (p.group_id=%s OR p.visible = 2)"
            else:
                sql += "WHERE ((p.group_id=%s AND p.visible <> 0) OR p.visible = 2)"
        else:
            if data['is_admin']:
                sql += "WHERE p.group_id=%s"
            else:
                sql += "WHERE p.group_id=%s AND p.visible <> 0"
        res = yield from self.db.execute(sql, (data['group_id'],))
        self.rs.set('problem_list_count@%s@%s'
                % (str(data['is_admin']), str(data['group_id'])), res[0]['COUNT(*)'])
        return (None, res[0]['COUNT(*)'])

    def get_problem(self, data={}):
        required_args = ['group_id', 'id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)

        if int(data['id']) == 0:
            col = ["id", "title", "description", "input", "output", "sample_input", "sample_output", "hint", "source", "group_id", "setter_user_id", "visible", "interactive", "checker_id", "created_at", "updated_at"]
            res = { x: "" for x in col }
            res['id'] = 0
            res['visible'] = 0
            return (None, res)

        res = self.rs.get('problem@%s' % str(data['id']))
        if not res:
            sql = "SELECT p.*, u.account as setter_user FROM problems as p, users as u WHERE p.setter_user_id=u.id AND p.id=%s"
            res = yield from self.db.execute(sql, (data["id"]))
            if len(res) == 0:
                return ('Error problem id', None)
            res = res[0]
            if int(res['group_id']) != int(data['group_id']) and int(res['visible']) != 2:
                return ('Error mapping problem id and group id', None)
            self.rs.set('problem@%s' % str(data['id']), res)
        err, res['execute'] = yield from self.get_problem_execute(data)
        err, res['testdata'] = yield from self.get_problem_testdata(data)
        return (None, res)

    def reset_rs_problem_count(self, group_id):
        self.rs.delete('problem_list_count@0@%s' % str(group_id))
        self.rs.delete('problem_list_count@1@%s' % str(group_id))
        """ public """
        self.rs.delete('problem_list_count@0@1' % str(group_id))
        self.rs.delete('problem_list_count@1@1' % str(group_id))

    def post_problem(self, data={}):
        required_args = ['id', 'group_id', 'setter_user_id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        self.reset_rs_problem_count(data['group_id'])
        if int(data['id']) == 0:
            data.pop('id')
            sql, parma = self.gen_insert_sql("problems", data)
            insert_id = yield from self.db.execute(sql, parma)
            return (None, insert_id)
        else:
            id = data['id']
            data.pop('id')
            self.rs.delete('problem@%s' % str(id))
            sql, parma = self.gen_update_sql("problems", data)
            yield from self.db.execute("%s WHERE id = %s" % (sql, id), parma)
            return (None, id)

    def delete_problem(self, data={}):
        required_args = ['id', 'group_id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        self.reset_rs_problem_count(data['group_id'])
        yield from self.db.execute("DELETE FROM problems WHERE id=%s", (int(data['id'])))
        self.rs.delete('problem@%s' % str(data['id']))
        return (None, None)

    def get_problem_execute(self, data={}):
        required_args = ['id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        res = self.rs.get('problem@%s@execute' % str(data['id']))
        if res: return (None, res)
        res = yield from self.db.execute("SELECT e.* FROM execute_types as e, (SELECT execute_type_id as id FROM map_problem_execute WHERE problem_id=%s) as b WHERE e.id=b.id ORDER BY e.id", (data['id'],))
        self.rs.set('problem@%s@execute' % str(data['id']), res)
        return (None, res)

    def post_problem_execute(self, data={}):
        self.rs.delete('problem@%s@execute' % str(data['id']))
        yield from self.db.execute("DELETE FROM map_problem_execute WHERE problem_id=%s", (data['id'],))
        """ Use try-except for process UNIQUE for execute_type_id-problem_id"""
        for x in data['execute']:
            yield from self.db.execute("INSERT IGNORE INTO map_problem_execute (`execute_type_id`, `problem_id`) values (%s, %s)", (x, data['id']))
        return (None, None)
    

    def get_problem_testdata_list(self, data={}):
        required_args = ['id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        res = self.rs.get('problem@%s@testdata' % str(data['id']))
        if res: return (None, res)
        res = yield from self.db.execute("SELECT t.* FROM testdata as t, (SELECT id FROM testdata WHERE problem_id=%s) as t2 where t.id=t2.id ORDER BY t.id ASC", (data['id']))
        self.rs.set('problem@%s@testdata' % str(data['id']), res)
        return (None, res)

    def get_problem_testdata(self, data={}):
        required_args = ['id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        res = self.rs.get('problem@%s@testdata' % str(data['id']))
        if res: return (None, res)
        res = yield from self.db.execute("SELECT t.* FROM testdata as t, (SELECT id FROM testdata WHERE problem_id=%s) as t2 where t.id=t2.id ORDER BY t.id ASC", (data['id']))
        self.rs.set('problem@%s@testdata' % str(data['id']), res)
        return (None, res)

    def post_problem_testdata(self, data={}):
        required_args = ['id', 'testdata_id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        self.rs.delete('problem@%s@testdata' % str(data['id']))
        if int(data['testdata_id']) == 0:
            id = yield from self.db.execute("INSERT INTO testdata (`problem_id`) VALUES (%s)", (data['id'],));
            return (None, id)
        else:
            required_args = ['time_limit', 'memory_limit', 'output_limit', 'score']
            err = self.check_required_args(required_args, data)
            if err: return (err, None)
            meta = { x: data[x] for x in required_args }
            sql, parma = self.gen_update_sql("testdata", meta)
            yield from self.db.execute("%s WHERE id=%s" % (sql, data['testdata_id']), parma)
            return (None, data['testdata_id'])

    def delete_problem_testdata(self, data={}):
        required_args = ['testdata_id']
        err = self.check_required_args(required_args, data)
        if err: return (err, None)
        self.rs.delete('problem@%s@testdata' % str(data['id']))
        yield from self.db.execute("DELETE FROM testdata WHERE id=%s", (data['testdata_id'],))
        return (None, None)
