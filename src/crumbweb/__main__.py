"""Front-end/back-end connector"""

from node_definitions import get_input_definition, get_output_definition, get_node_definition
from html_templates import function_list_as_html, NAV_TYPES
from sessions import SessionStore

import string
import random
import base64
import os
import json
import tornado
import tornado.ioloop
import tornado.web
import tornado.template

loader = tornado.template.Loader('.')

STATIC_PATH = '../../dist/'
INDEX_FILE = 'index.html'
SLICE_FILE = 'slice.html'
SETTINGS = {
    "cookie_secret": base64.b64encode(os.urandom(50)).decode('ascii'),
    "login_url": "/login",
    'debug': False
}
if 'BREADR_PWD' in os.environ:
    print('Using environment password BREADR_PWD')
    BREADR_PASSWORD = os.environ['BREADR_PWD']
else:
    _ops = string.ascii_letters + string.digits
    BREADR_PASSWORD = ''.join([random.choice(_ops) for _ in range(16)])
TREE_FILE = 'tree.html'

a = 0


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        pwd = self.get_secure_cookie('password')
        if not pwd:
            return None
        return tornado.escape.json_decode(pwd)


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(INDEX_FILE)


class TreeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path):
        print(f'path is "{path}"')
        if path == '':
            path = '.'

        def isbreadr(x):
            return x.split('.')[-1] == 'json'

        def get_namelink(x):
            if isbreadr(x):  # we can open
                link = f'/slice/{os.path.join(path, x)}'
                return f"""<a href="{link}">{x}</a>"""
            elif os.path.isfile(x):  # we do not open
                return x
            # folder
            link = f'/tree/{os.path.join(path, x)}'
            return f"""<a href="{link}">{x}</a>"""
        
        _reported_folders = [f for f in ['..'] + os.listdir(path) if f[0] != '_' and not(f[0] == '.' and f[1] != '.') and not(f == '..' and path == '.')]
        filefolders = {f: {'type': NAV_TYPES['breadr'] if isbreadr(f) else NAV_TYPES['file'] if os.path.isfile(f) else NAV_TYPES['folder'],
                           'name': get_namelink(f),
                           'size': '',
                           'modified': ''} for f in _reported_folders}
        r = loader.load(TREE_FILE).generate(filefolders=filefolders)
        self.write(r)


class LoginHandler(BaseHandler):
    def get(self):
        password = self.get_argument("password", "")
        auth = self.check_permission(password)
        if auth:
            self.set_current_user(password)
            self.redirect(self.get_argument("next", u"/"))
        else:
            params = {
                "errormessage": self.get_argument("error", ''),
                "nextpage": self.get_argument("next", "/")
            }
            self.render('login.html', **params)

    def check_permission(self, password):
        if password == BREADR_PASSWORD:
            return True
        return False

    def post(self):
        password = self.get_argument("password", "")
        auth = self.check_permission(password)
        if auth:
            self.set_current_user(password)
            self.redirect(self.get_argument("next", u"/"))
        else:
            self.redirect(u"/login" + u"?error=" + tornado.escape.url_escape("Invalid password!"))

    def set_current_user(self, password):
        if password:
            self.set_secure_cookie("password", tornado.escape.json_encode(password))
        else:
            self.clear_cookie("password")


class SliceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, file):
        r = loader.load(SLICE_FILE).generate(file=file)
        self.write(r)


class addNode(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)

        x_pos = data['payload']['ele_pos_x']
        y_pos = data['payload']['ele_pos_y']

        global a
        a = a + 1

        ret = {}

        match data['payload']['name']:
            case 'input_element':
                ret = get_input_definition(a, x_pos, y_pos, f'input_{a}')
            case 'output_element':
                ret = get_output_definition(a, x_pos, y_pos, f'output_{a}')
            case 'multiple_element':
                icon_str = "fas fa-code-branch"
                inputs = {'in1': int, 'in2': str}
                outputs = {'out1': str, 'out2': int}
                description = "\n\n\n\n"
                name = 'crumbcrumbcrumb'
                ret = get_node_definition(a, name, x_pos, y_pos, inputs, outputs, icon=icon_str, node_description=description)
            case _:
                'error?'

        ret['operation'] = 'addNode'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class removeNodeId(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        ret = {'id': data['payload']['id']}
        SessionStore.get_file(data['payload']['file']).removeNode(**ret)
        ret['operation'] = 'removeNodeId'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class addConnection(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        try:
            # make changes
            ret = {'id_output': data['payload']['id_output'],
                   'id_input': data['payload']['id_input'],
                   'output_class': data['payload']['output_class'],
                   'input_class': data['payload']['input_class']}
            SessionStore.get_file(data['payload']['file']).addConnection(**ret)
            ret['operation'] = 'addConnection'
            print(data, '===>', ret)
            r = json.dumps(ret)
            self.write(r)
        except Exception as e:
            self.set_status(400)
            self.write({'error': e})


class removeConnection(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        ret = {'class_list': data['payload']['class_list']}
        SessionStore.get_file(data['payload']['file']).removeConnection(**ret)
        ret['operation'] = 'removeConnection'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class nodeMoved(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        SessionStore.get_file(data['payload']['file']).move_node(id=data['payload']['id'], x=data['payload']['pos_x'], y=data['payload']['pos_y'])
        ret = {'operation': 'nodeMoved'}
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class zoom(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        SessionStore.get_file(data['payload']['file']).zoom(data['payload']['zoom'])
        ret = {'operation': 'zoom'}
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class translate(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        SessionStore.get_file(data['payload']['file']).translate(data['payload']['x'], data['payload']['y'])
        ret = {'operation': 'translate'}
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class refresh(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        ret = {'html': function_list_as_html(SessionStore.get_file(data['payload']['file']).get_function_list())}
        ret['operation'] = 'refresh'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class run(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        all_output = SessionStore.get_file(data['payload']['file']).run()
        ret = {'output': all_output}
        ret['operation'] = 'run'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class setParameter(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        ret = {'node': data['payload']['node'], 'name': data['payload']['name'], 'type': data['payload']['type']}
        SessionStore.get_file(data['payload']['file']).setParameter(**ret)
        ret['operation'] = 'setParameter'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


class save(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        SessionStore.get_file(data['payload']['file']).save()
        ret = {'status': 'ok'}
        ret['operation'] = 'save'
        print(data, '===>', ret)
        r = json.dumps(ret)
        self.write(r)


def main():
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/tree/(.*)", TreeHandler),
        (r"/slice/(.*)", SliceHandler),
        (r"/api/v1/addNode", addNode),
        (r"/api/v1/removeNodeId", removeNodeId),
        (r"/api/v1/addConnection", addConnection),
        (r"/api/v1/removeConnection", removeConnection),
        (r"/api/v1/nodeMoved", nodeMoved),
        (r"/api/v1/zoom", zoom),
        (r"/api/v1/translate", translate),
        (r"/api/v1/refresh", refresh),
        (r"/api/v1/setParameter", setParameter),
        (r"/api/v1/save", save),

        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "../../"}),
        (r'/dist/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH})
    ], **SETTINGS)
    app.listen(8080, '127.0.0.1')
    print(f'Connect using: http://127.0.0.1:8080/login?password={BREADR_PASSWORD}')
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
