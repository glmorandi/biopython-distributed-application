from tcp_server import TCPServer

def start_server():
    """
    Inicia um servidor TCP na porta 31337 e no host 127.0.0.1.
    """
    host = "127.0.0.1"
    port = 31337
    server = TCPServer(host, port)
    server.start()
    
if __name__ == "__main__":
    start_server()
