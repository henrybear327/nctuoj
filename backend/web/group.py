from req import WebRequestHandler
from req import Service
import tornado
import math

class WebGroupHandler(WebRequestHandler):
    @tornado.gen.coroutine
    def get(self, id):
        self.redirect('/groups/%s/bulletins/'%(id))

class WebGroupManageHandler(WebRequestHandler):
    @tornado.gen.coroutine
    def get(self, id, action):
        err, data = yield from Service.Group.get_group({"id": id})
        if data['type'] == 1: #inpublic
            err, data['inpublic'] = yield from Service.Group.get_inpublic_group_user({'id': id})
        if not action:
            action = "basic/"
        if action == "basic/":
            self.render('group/group_manage_basic.html', data=data)
        elif action == "member/":
            self.render('group/group_manage_member.html', data=data)
        else:
            self.write_error(404)

class WebGroupsHandler(WebRequestHandler):
    @tornado.gen.coroutine
    def get(self):
        args = ["page"]
        meta = self.get_args(args)
        meta['count'] = 100
        ### default page is 1
        if not meta['page']:
            meta['page'] = 1
        ### if get page is not int then redirect to page 1 
        try:
            meta["page"] = int(meta["page"])
        except:
            self.write_error((500, 'Argument page error'))
            return
        ### should in range
        err, count = yield from Service.Group.get_group_list_count()
        page_count = max(math.ceil(count / int(meta['count'])), 1)
        if int(meta['page']) < 1 or int(meta['page']) > page_count:
            self.write_error((500, 'Page out of range'))
            return
        ### get data
        err, data = yield from Service.Group.get_group_list(meta)
        ### about pagination 
        page = {}
        page['total'] = page_count
        page['current'] = meta['page']
        page['url'] = '/groups/'
        page['get'] = {}
        self.render('./group/groups.html', data=data, page=page)

