import tornado.ioloop
import tornado.web
import json

class UVHandler(tornado.web.RequestHandler):
    uv_data = None  # atributo da classe para armazenar os dados enviados via POST

    def get(self):
        if self.uv_data is not None:
            self.write({"message": "Latest UV Reading", "uv": self.uv_data})
        else:
            self.set_status(404)
            self.write({"error": "No UV data available"})

    def post(self):
        data_json = self.request.body.decode('utf-8')
        data = json.loads(data_json)
        uv_reading = data.get('uv', None)
        if uv_reading is not None:
            print("UV Reading: ", uv_reading)
            self.uv_data = uv_reading  # armazena o dado enviado via POST
            self.set_status(200)
            self.write({"message": "UV Reading received"})
        else:
            self.set_status(400)
            self.write({"error": "Invalid data, 'uv' key not found"})

def make_app():
    return tornado.web.Application([
        (r"/uv", UVHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    print("Server is running...")  # Adiciona mensagem de aviso
    tornado.ioloop.IOLoop.current().start()
