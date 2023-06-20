import tornado.ioloop
import tornado.web
import json

uv_data = None

class UVHandler(tornado.web.RequestHandler):
    def get(self):
        global uv_data
        if uv_data is not None:
            self.write("""
            <html>
            <body>
                <h1>Latest UV Reading</h1>
                <div id="uvValue">{}</div>
                <script>
                    setInterval(function() {{
                        fetch('/uvValue')
                            .then(response => response.json())
                            .then(data => {{
                                document.getElementById('uvValue').textContent = data.uv;
                            }});
                    }}, 2000); // atualiza a cada 2 segundos
                </script>
            </body>
            </html>
            """.format(uv_data))
        else:
            self.set_status(404)
            self.write({"error": "No UV data available"})

    def post(self):
        global uv_data
        data_json = self.request.body.decode('utf-8')
        data = json.loads(data_json)
        uv_reading = data.get('uv', None)
        if uv_reading is not None:
            print("UV Reading: ", uv_reading)
            uv_data = uv_reading
            self.set_status(200)
            self.write({"message": "UV Reading received"})
        else:
            self.set_status(400)
            self.write({"error": "Invalid data, 'uv' key not found"})

class UVValueHandler(tornado.web.RequestHandler):
    def get(self):
        global uv_data
        if uv_data is not None:
            self.write({"uv": uv_data})
        else:
            self.set_status(404)
            self.write({"error": "No UV data available"})

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.finish()

def make_app():
    return tornado.web.Application([
        (r"/uv", UVHandler),
        (r"/uvValue", UVValueHandler),
        (r"/favicon.ico", FaviconHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    print("Server is running...")
    tornado.ioloop.IOLoop.current().start()
