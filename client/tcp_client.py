import socket
import os

class TCPClient:
    """Classe que representa um cliente TCP.

    Parametros:
        host (str): O endereço IP do servidor.
        port (int): A porta do servidor.
        server_socket (socket): O socket do servidor.

    Métodos:
        connect(): Conecta o cliente ao servidor.
        send_mode(mode: str): Envia o modo de operação para o servidor.
        send_parallel(parallel: str): Envia o número de paralelismo para o servidor.
        upload_file(file_path: str): Envia um arquivo para o servidor.
        download_file(file_path: str): Recebe um arquivo do servidor.
        close(): Fecha a conexão com o servidor.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
    
    def connect(self):
        """Conecta o cliente ao servidor."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.host, self.port))
        except Exception as e:
            print(f"Erro ao conectar com o servidor: {e}")
            self.server_socket.close()

    def send_mode(self, mode):
        """Envia o modo de operação para o servidor.

        Parametros:
            mode (str): O modo de operação.

        Errors:
            ConnectionError: Se houver um erro de conexão.
        """
        try:
            self.server_socket.send(mode.encode("utf-8"))
        except Exception as e:
            print(f"Erro ao enviar o modo de operação para o servidor: {e}")
            self.server_socket.close()
            exit()

    def send_parallel(self, parallel):
        """Envia o número de paralelismo para o servidor.

        Parametros:
            parallel (str): O número de paralelismo.

        Errors:
            ConnectionError: Se houver um erro de conexão.
        """
        try:
            self.server_socket.send(parallel.encode("utf-8"))
        except Exception as e:
            print(f"Erro ao enviar número de paralelismo para o servidor: {e}")
            self.server_socket.close()
            exit()

    def upload_file(self, file_path):
        """Envia um arquivo para o servidor.

        Parametros:
            file_path (str): O caminho do arquivo.

        Errors:
            FileNotFoundError: Se o arquivo não for encontrado.
            ConnectionError: Se houver um erro de conexão.
        """
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
        """Recebe um arquivo do servidor.

        Parametros:
            file_path (str): O caminho do arquivo.

        Errors:
            ConnectionError: Se houver um erro de conexão.
        """
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
        """Fecha a conexão com o servidor."""
        if self.server_socket:
            self.server_socket.close()
