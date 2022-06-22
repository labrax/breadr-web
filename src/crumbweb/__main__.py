import json
import tornado
import tornado.ioloop
import tornado.web
import tornado.template

loader = tornado.template.Loader('.')

static_path_dir = '../../dist/'
index_file = 'index.html'
slice_file = 'slice.html'
a = 0


from node_definitions import get_input_definition, get_output_definition, get_node_definition
from functions import get_function_list

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(index_file)


class SliceHandler(tornado.web.RequestHandler):
    def get(self, file):
        r = loader.load(slice_file).generate(file=file)
        # print(r)
        self.write(r)


class addConnection(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        try:
            # make changes
            r = json.dumps({'id_output': data['payload']['id_output'], 
                            'id_input': data['payload']['id_input'], 
                            'output_class': data['payload']['output_class'], 
                            'input_class': data['payload']['input_class']})
            self.write(r)
        except Exception as e:
            self.set_status(400)
            self.write({'error': e})


class removeConnection(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({'class_list': data['payload']['class_list']})
        self.write(r)


class addNode(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)

        x_pos = data['payload']['ele_pos_x']
        y_pos = data['payload']['ele_pos_y']

        global a
        a = a + 1

        match data['payload']['name']:
            case 'input_element':
                ret = get_input_definition(a, x_pos, y_pos, f'input_{a}')
            case 'output_element':
                ret = get_output_definition(a, x_pos, y_pos, f'output_{a}')
            case 'multiple_element':
                icon_str = "fas fa-code-branch"
                inputs =  {'in1': int, 'in2': str}
                outputs =  {'out1': str, 'out2': int}
                description="\n\n\n\n"
                name = 'crumbcrumbcrumb'
                ret = get_node_definition(a, name, x_pos, y_pos, inputs, outputs, icon=icon_str, node_description=description)
            case _:
                'error?'

        print(ret)

        r = json.dumps(ret)
        self.write(r)


class removeNodeId(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({'id': data['payload']['id']})
        self.write(r)


class nodeMoved(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({})
        self.write(r)


class zoom(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({})
        self.write(r)


class translate(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({})
        self.write(r)


class refresh(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        r = json.dumps({'html': get_function_list()})
        self.write(r)


class run(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        # TODO: implement
        r = json.dumps({})
        self.write(r)


class setParameter(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        # TODO: implement
        # check if we good changing? aka: anything connected here? no duplicates?
        r = json.dumps({'node': data['payload']['node'], 'name': data['payload']['name'], 'type': data['payload']['type']})
        self.write(r)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
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

        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "../../"}),
        (r'/dist/(.*)', tornado.web.StaticFileHandler, {'path': static_path_dir})
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
