import socket
import os
import sys 
sys.path.append(".")

from processing.processing import Sequential, OpenMP, Multithread, Multiprocess

class TCPServer:
    """ TCP Server """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        try:
            self.clean()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Servidor está conectado em: {self.host}:{self.port}")
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Aceita conexão de: {client_address[0]}:{client_address[1]}")
                self.handle_client(client_socket, client_address)
        except Exception as e:
            print(f"Erro de servidor: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        try:
            # Recebe o modo de operção do client
            print(f"Recebendo o modo de operação de: {client_address[0]}:{client_address[1]}")
            mode = int(client_socket.recv(1024).decode("utf-8"))

            print(f"Recebendo o número de threads/procesos para utilizar de: {client_address[0]}:{client_address[1]}")

            # Recebe o número de threads/procesos para utilizar
            parallel = int(client_socket.recv(1024).decode("utf-8"))
            
            print(f"Recebendo o arquivo de: {client_address[0]}:{client_address[1]}")
            # Recebe o arquivo
            self.download_file(client_socket)

            print(f"Inicializando o processamento para: {client_address[0]}:{client_address[1]}")

            if mode == 1:
                seq = Sequential("received", "temp.fasta", "aligned.txt")
                seq.process()
                self.upload_file(client_socket)
                seq.cleanup_files()
            elif mode == 2:
                multi = Multithread("received", "temp.fasta", "aligned.txt", parallel)
                multi.process()
                self.upload_file(client_socket)
                multi.cleanup_files()
            elif mode == 3:
                proc = Multiprocess("received", "temp.fasta", "aligned.txt", parallel)
                proc.process()
                self.upload_file(client_socket)
                proc.cleanup_files()
            elif mode == 4:
                omp = OpenMP("received", "temp.fasta", "aligned.txt", parallel)
                omp.process()
                self.upload_file(client_socket)
                omp.cleanup_files()
            else:
                print("Nenhum dado recebido do client")
                client_socket.close()
            
            print(f"Finalizado o processamento para: {client_address[0]}:{client_address[1]}, terminando a conexão")
            print("Realizando a limpeza")
            self.clean()
            client_socket.send("Operação concluída, finalizando conexão".encode("utf-8"))
            client_socket.close()

        except Exception as e:
            print(f"Erro com o client: {e}")

    def clean(self):
        if os.path.exists("aligned.txt"):
            os.remove("aligned.txt")
        if os.path.exists("received"):
            os.remove("received")

    def download_file(self, client_socket):
        try:
            file_size_str = client_socket.recv(1024).decode()

            file_size = int(file_size_str)

            save_path = "received"

            with open(save_path, 'wb') as file:
                received_data = b""
                while len(received_data) < file_size:
                    remaining_size = file_size - len(received_data)
                    chunk = client_socket.recv(1024 if remaining_size > 1024 else remaining_size)
                    if not chunk:
                        break
                    received_data += chunk
                file.write(received_data)

            print(f"Arquivo recebido e salvo: '{save_path}'.")
        except ConnectionError as ce:
            print(f"Erro de conexão: {ce}")
        except Exception as e:
            print(f"Erro ao receber o arquivo: {e}")

    def upload_file(self, client_socket):
        try:
            file_path = "aligned.txt"
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    client_socket.send(file_data)
                file.close()
                print("Arquivo enviado para o cliente")
            else:
                print(f"Arquivo '{file_path}' não encontrado.")

        except ConnectionError as ce:
            print(f"Erro de conexão: {ce}")
        except Exception as e:
            print(f"Erro ao enviar arquivo para o cliente: {e}")