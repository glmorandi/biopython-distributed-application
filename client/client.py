from tcp_client import TCPClient

def main():
    """
    Função principal que inicia o cliente TCP e envia um arquivo para o servidor.

    O usuário deve digitar o modo de operação desejado (sequencial, multithread, OpenMP ou multiprocess),
    a quantidade de threads/processos para utilizar, o local do arquivo para ser enviado e o local do arquivo
    para ser recebido.
    """
    host = "127.0.0.1"
    port = 31337
    client = TCPClient(host, port)
    client.connect()

    modo = (input("Digite o modo de operação desejado:\n\n1.Sequencial\n2.Multithread\n3.OpenMP\n4.Multiprocess\n"))

    client.send_mode(modo)
    
    parallel = (input("Digite a quantidade de threads/processos para utilizar:"))

    client.send_parallel(parallel)

    file = input("Digite o local do arquivo para ser enviado:")

    rec = input("Digite o local do arquivo para ser recebido:")

    print("Enviando o arquivo para o servidor")

    client.upload_file(file)

    print("Recebendo arquivo do servidor")

    client.download_file(rec)

    client.close()
    
    exit()

if __name__ == "__main__":
    main()
