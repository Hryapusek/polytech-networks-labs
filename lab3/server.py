from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>Привет! Это мой HTTP-сервер на Python</h1>".encode("utf-8"))
        elif self.path == "/about":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Это простая страница About".encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Страница не найдена".encode("utf-8"))

host = "localhost"
port = 8080

server = HTTPServer((host, port), MyHTTPRequestHandler)
print(f"Сервер запущен на http://{host}:{port}")
server.serve_forever()
