import os
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler


class MyHandler(BaseHTTPRequestHandler):
    server_version = "TestServer/1.0"
    ErrorPage = \
"""
<html>
<body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
</body>
</html>
"""


    def do_GET(self):
        try:
            fullPath = os.getcwd() + "/content" + self.path

            if not os.path.exists(fullPath):
                raise Exception("'%s' not found" % (self.path))
            elif os.path.isfile(fullPath):
                self.handleFile(fullPath)
            else:
                raise Exception("unknown object '%s'" % (self.path))
        except Exception as ex:
            self.handleError(ex)


    def handleFile(self, path):
        try:
            with open(path, 'rb') as reader:
                content = reader.read()
                self.sendContent(content)
        except IOError as ex:
            self.handleError("read '%s' error: %s" % (self.path, ex))


    def handleError(self, ex):
        content = self.ErrorPage.format(path=self.path, msg=ex)
        self.sendContent(bytes(content, encoding="utf-8"), 404)


    def sendContent(self, page, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)


if __name__ == "__main__":
    serverAddr = ('', 8080)
    server = HTTPServer(serverAddr, MyHandler)
    server.serve_forever()
