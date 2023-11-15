from Bio import SeqIO, Align
import os
import threading
import multiprocessing
#from numba.openmp import openmp_context as openmp

class Processing:
    """
    Classe responsável por processar arquivos de sequências genéticas.

    Parametros:
    ----------
    input_file : str
        Caminho para o arquivo de entrada contendo as sequências genéticas no formato GenBank.
    temp_file : str
        Caminho para o arquivo temporário que será criado durante o processamento.
    output_file : str
        Caminho para o arquivo de saída que conterá as sequências genéticas no formato FASTA.

    Métodos:
    -------
    convert_genbank_to_fasta()
        Converte as sequências genéticas do arquivo de entrada no formato GenBank para o formato FASTA e as salva no arquivo temporário.
    cleanup_files()
        Remove os arquivos temporário e de saída criados durante o processamento.
    """
    def __init__(self, input_file, temp_file, output_file):
        self.input_file = input_file
        self.temp_file = temp_file
        self.output_file = output_file

    def convert_genbank_to_fasta(self):
        """
        Converte as sequências genéticas do arquivo de entrada no formato GenBank para o formato FASTA e as salva no arquivo temporário.
        """
        sequences = SeqIO.parse(self.input_file, "genbank")
        SeqIO.write(sequences, self.temp_file, "fasta")

    def cleanup_files(self):
        """
        Remove os arquivos temporário e de saída criados durante o processamento.
        """
        os.remove(self.temp_file)
        os.remove(self.output_file)
        
class Sequential(Processing):
    """
    Classe que realiza o processamento de dados de modo sequencial.
    Herda da classe Processing e implementa o método abstrato process().

    Métodos:
    ---------
    perform_alignment():
        Realiza o alinhamento de sequências utilizando o módulo Align do Biopython.
        Salva o resultado do alinhamento em um arquivo de saída.

    process():
        Método abstrato implementado da classe pai Processing.
        Chama os métodos convert_genbank_to_fasta() e perform_alignment() para realizar o processamento de dados.
    """
    
    def perform_alignment(self):
        """
        Realiza o alinhamento de sequências utilizando o módulo Align do Biopython.
        Salva o resultado do alinhamento em um arquivo de saída.
        """
        aligner = Align.PairwiseAligner()
        alignments = []
        
        sequences = list(SeqIO.parse(self.temp_file, "fasta"))

        for i in range(len(sequences)):
            for j in range(i+1, len(sequences)):
                alignment = aligner.align(sequences[i].seq, sequences[j].seq)

                alignments.extend([alignment[0].__format__("fasta"), alignment[1].__format__("fasta")])

        with open(self.output_file, "w") as file:
            for aligned_pair in alignments:
                file.write(str(aligned_pair) + "\n")
            file.close()

    def process(self):
        """
        Método abstrato implementado da classe pai Processing.
        Chama os métodos convert_genbank_to_fasta() e perform_alignment() para realizar o processamento de dados.
        """
        self.convert_genbank_to_fasta()
        self.perform_alignment()

class Parallel(Processing):
    """ 
    Classe que realiza o processamento de dados de modo paralelo. Herda da classe Processing.

    Parametros:
        input_file (str): Caminho para o arquivo de entrada.
        temp_file (str): Caminho para o arquivo temporário.
        output_file (str): Caminho para o arquivo de saída.
        parallel (int): Número de processos paralelos.

    Métodos:
        convert_genbank_to_fasta(): Converte o arquivo de entrada do formato GenBank para o formato Fasta.
        join_files(): Concatena os arquivos temporários gerados pelo método convert_genbank_to_fasta().
        cleanup_files(): Remove os arquivos temporários gerados pelo método convert_genbank_to_fasta().
        perform_alignment(i): Realiza o alinhamento de sequências do arquivo temporário i.
    """

    def __init__(self, input_file, temp_file, output_file, parallel=4):
        super().__init__(input_file, temp_file, output_file)
        self.parallel = parallel

    def convert_genbank_to_fasta(self):
        """
        Converte o arquivo de entrada do formato GenBank para o formato Fasta.
        Divide o arquivo em partes e escreve cada parte em um arquivo temporário.
        """
        sequences = SeqIO.parse(self.input_file, "genbank")

        output_files = [f"{self.temp_file}_{i}" for i in range(self.parallel)]
    
        output_handles = [open(file, "w") for file in output_files]
    
        for i, record in enumerate(sequences):
            output_handles[i % self.parallel].write(">" + record.id + "\n" + str(record.seq) + "\n")
            
        for handle in output_handles:
            handle.close()

    def join_files(self):
        """
        Concatena os arquivos temporários gerados pelo método convert_genbank_to_fasta().
        Escreve o resultado no arquivo de saída.
        """
        file_contents = []

        for i in range(self.parallel):
            with open(f"{self.output_file}_{i}", 'r') as file:
                file_contents.append(file.read())

        joined = "".join(file_contents)

        with open(self.output_file, 'w') as output_file:
            output_file.write(joined)

    def cleanup_files(self):
        """
        Remove os arquivos temporários gerados pelo método convert_genbank_to_fasta().
        """
        for i in range(self.parallel):
            os.remove(f"{self.temp_file}_{i}")

        for i in range(self.parallel):
            os.remove(f"{self.output_file}_{i}")
    
    def perform_alignment(self, i):
        """
        Realiza o alinhamento de sequências do arquivo temporário i.
        Escreve o resultado no arquivo de saída correspondente.
        
        Parametros:
            i (int): Índice do arquivo temporário a ser processado.
        """
        aligner = Align.PairwiseAligner()
        alignments = []
        
        sequences = list(SeqIO.parse(f"{self.temp_file}_{i}", "fasta"))

        for j in range(len(sequences)):
            for k in range(j+1, len(sequences)):
                alignment = aligner.align(sequences[j].seq, sequences[k].seq)

                alignments.extend([alignment[0].__format__("fasta"), alignment[k].__format__("fasta")])

        with open(f"{self.output_file}_{i}", "w") as file:
            for aligned_pair in alignments:
                file.write(str(aligned_pair) + "\n")
            file.close()

class Multithread(Parallel):
    """Realiza o processamento de dados utilizando threads.

    Esta classe herda da classe `Parallel` e implementa o método `process` para realizar o processamento
    de dados utilizando threads.

    Métodos:
    --------
    process()
        Realiza o processamento de dados utilizando threads.
    """

    def process(self):
        """Realiza o processamento de dados utilizando threads.

        Este método realiza o processamento de dados utilizando threads. Ele converte o arquivo GenBank para
        o formato Fasta e, em seguida, cria uma thread para cada processador disponível no sistema. Cada thread
        executa o método `perform_alignment` da classe `Parallel` com um índice diferente. Por fim, as threads
        são aguardadas para que o processo seja finalizado e os arquivos gerados sejam unidos em um único arquivo.
        """
        threads = []

        self.convert_genbank_to_fasta()

        for i in range(self.parallel):
            align_thread = threading.Thread(target=self.perform_alignment, args=(i,))
            threads.extend([align_thread])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

        self.join_files()

class OpenMP(Parallel):
    """
    Classe que implementa o processamento de dados utilizando OpenMP.

    Esta classe herda da classe Parallel e implementa o método process, que é responsável por realizar o processamento
    dos dados utilizando OpenMP.

    Métodos:
    --------
    process():
        Realiza o processamento dos dados utilizando OpenMP.
    """

    def process(self):
        """
        Realiza o processamento dos dados utilizando OpenMP.

        Este método é responsável por realizar o processamento dos dados utilizando OpenMP. Ele chama o método
        convert_genbank_to_fasta para converter os arquivos genbank em arquivos fasta, realiza o alinhamento dos
        arquivos fasta utilizando OpenMP e, por fim, junta os arquivos alinhados em um único arquivo.
        """

        self.convert_genbank_to_fasta()

        #with openmp("parallel"):
        #    with openmp("schedule(static)"):
        #        for i in range(self.parallel):
        #            self.perform_alignment(i)

        self.join_files()
    
class Multiprocess(Parallel):
    """ 
    Classe que realiza o processamento de dados utilizando processos.

    Esta classe herda da classe Parallel e implementa os métodos necessários para realizar o processamento
    de dados utilizando processos.

    Parametros:
    ----------
    parallel : int
        Número de processos a serem utilizados.
    input_file : str
        Caminho para o arquivo de entrada.
    output_file : str
        Caminho para o arquivo de saída.
    aligner : str
        Nome do alinhador a ser utilizado.
    aligner_path : str
        Caminho para o executável do alinhador.
    """

    def process(self):
        """ 
        Realiza o processamento de dados utilizando processos.

        Este método realiza o processamento de dados utilizando processos. Ele converte o arquivo de entrada
        para o formato FASTA e, em seguida, inicia um processo para cada um dos alinhamentos a serem realizados.
        Por fim, ele junta os arquivos de saída gerados pelos processos em um único arquivo de saída.
        """
        processes = []

        self.convert_genbank_to_fasta()

        for i in range(self.parallel):
            align_process = multiprocessing.Process(target=self.perform_alignment, args=(i,))
            processes.extend([align_process])

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        self.join_files()