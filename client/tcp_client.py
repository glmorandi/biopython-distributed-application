import socket
import os

class TCPClient:
    """ TCP Client """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
    
    def connect(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.host, self.port))
        except Exception as e:
            print(f"Erro ao conectar com o servidor: {e}")
            self.server_socket.close()

    def send_mode(self, mode):
        try:
            self.server_socket.send(mode.encode("utf-8"))
        except Exception as e:
            print(f"Erro ao enviar o modo de operação para o servidor: {e}")
            self.server_socket.close()
            exit()

    def send_parallel(self, parallel):
        try:
            self.server_socket.send(parallel.encode("utf-8"))
        except Exception as e:
            print(f"Erro ao enviar número de paralelismo para o servidor: {e}")
            self.server_socket.close()
            exit()

    def upload_file(self, file_path):
            try:
                file_size = os.path.getsize(file_path)
                
                self.server_socket.send(str(file_size).encode())

                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    self.server_socket.sendall(file_data)

                print(f"Arquivo '{file_path}' enviado com sucesso.")
            except FileNotFoundError:
                print(f"Arquivo '{file_path}' não foi encontrado.")
            except ConnectionError as ce:
                print(f"Erro de conexão: {ce}")
            except Exception as e:
                print(f"Erro ao fazer upload para o servidor: {e}")

    def download_file(self, file_path):
        try:
            file_data = b""
            while True:
                data = self.server_socket.recv(1024)
                if not data:
                    break
                file_data += data

            if file_data:
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                file.close()
                print(f"Arquivo recebido: '{file_path}'")

            else:
                print("Nenhum dado recebido do cliente")

        except ConnectionError as ce:
            print(f"Erro de conexão: {ce}")
        except Exception as e:
            print(f"Erro ao receber o arquivo: {e}")


    def close(self):
        if self.server_socket:
            self.server_socket.close()
