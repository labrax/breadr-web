import json
import tornado
import tornado.ioloop
import tornado.web

static_path_dir = 'dist/'
index_file = 'index.html'
a = 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(open(index_file, mode='r', encoding='utf-8').read())


class AddNodeHandler(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        global a
        a = a + 1
        r = json.dumps({'node_id': a})
        self.write(r)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/v1/addNode", AddNodeHandler),
        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
        (r'/dist/(.*)', tornado.web.StaticFileHandler, {'path': static_path_dir})
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
