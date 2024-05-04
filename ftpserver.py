from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

HOST = "127.0.0.1"
PORT = 1026

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "D:\\candidates", perm="elradfmw")
authorizer.add_anonymous("D:\\candidates", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer((HOST, PORT), handler)
server.serve_forever()