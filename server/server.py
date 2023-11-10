from tcp_server import TCPServer

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 31337
    server = TCPServer(host, port)
    server.start()