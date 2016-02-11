from req import Service
from map import *
from service.base import BaseService
from utils.form import form_validation

class TagService(BaseService):
    def __init__(self, db, rs):
        super().__init__(db, rs)

        TagService.inst = self

    def get_tag_list(self):
        # res = self.rs.get('tag_list')
        # if res: return (None, res)
        res = yield self.db.execute('SELECT * FROM tags;')
        res = res.fetchall()
        print('RES: ',res)
        # self.rs.set('tag_list', res)
        return (None, res)

    def get_tag(self, data={}):
        required_args = [{
            'name': '+id',
            'type': int,
        }]
        err = form_validation(data, required_args)
        if err: return (err, None)
        # res = self.rs.get('tag@%s'%(str(data['id'])))
        res = yield self.db.execute('SELECT * FROM tags WHERE id=%s;', (data['id'],))
        if res.rowcount == 0:
            return ('No tag ID', None)
        res = res.fetchone()
        # self.rs.set('tag@%s'%(str(data['id'])), res)
        return (None, res)

    def post_tag(self, data={}):
        required_args = [{
            'name': '+id',
            'type': int,
        }, {
            'name': '+tag',
            'type': str,
        }]
        err = form_validation(data, required_args)
        if err: return (err, None)
        if int(data['id']) == 0:
            sql, param = self.gen_insert_sql('tags', data)
            id = yield self.db.execute(sql, param)
            id = id.fetchone()['id']
        else:
            id = data.pop('id')
            # self.rs.delete('tag@%s'%(id))
            sql ,param = self.gen_update_sql('tags', data)
            yield self.db.execute(sql, param)
        return (None, id)

    def delete_tag(self, data={}):
        required_args = ['id']
        required_args = [{
            'name': '+id',
            'type': int,
        }]
        # err = self.check_required_args(required_args, data)
        err = form_validation(data, required_args)
        if err: return (err, None)
        # self.rs.delete('tag@%s'%(str(data['id'])))
        yield self.db.execute('DELETE FROM tags WHERE id=%s', (data['id'],))
        return (None, None)

    def post_problem_tag(self, data={}):
        required_args = ['tag_id', 'problem_id']
        required_args = [{
            'name': '+tag_id',
            'type': str,
        }, {
            'name': '+problem_id',
            'type': str,
        }]
        # err = self.check_required_args(required_args, data)
        err = form_validation(data, required_args)
        if err: return (err, None)
        # self.rs.delete('tag@problem@%s'%(data['problem_id']))
        try: yield self.db.execute('INSERT INTO map_problem_tag (tag_id, problem_id) VALUES(%s, %s);', (data['tag_id'], data['problem_id']))
        except: return ('Already in', None)
        return (None, None)

    def delete_problem_tag(self, data={}):
        required_args = ['tag_id', 'problem_id']
        required_args = [{
            'name': '+tag_id',
            'type': str,
        }, {
            'name': '+problem_id',
            'type': str,
        }]
        # err = self.check_required_args(required_args, data)
        err = form_validation(data, required_args)
        if err: return (err, None)
        # self.rs.delete('tag@problem@%s'%(data['problem_id']))
        res = yield self.db.execute('DELETE FROM map_problem_tag WHERE tag_id=%s AND problem_id=%s RETURNING id;', (data['tag_id'], data['problem_id']))
        if res.rowcount == 0:
            return ('no this tag in this problem', None)
        return (None, None)

    def get_problem_tag(self, data={}):
        required_args = ['problem_id']
        required_args = [{
            'name': '+problem_id',
            'type': int,
        }]
        # err = self.check_required_args(required_args, data)
        err = form_validation(data, required_args)
        if err: return (err, None)
        # res = self.rs.get('tag@problem@%s'%(str(data['problem_id'])))
        # if res: return (None, res)
        res = yield self.db.execute('SELECT t.* FROM tags as t, map_problem_tag as m WHERE m.tag_id=t.id AND m.problem_id=%s;', (data['problem_id'],))
        res = res.fetchall()
        print('RES: ', res)
        # self.rs.set('tag@problem@%s'%(str(data['problem_id'])), res)
        return (None, res)
