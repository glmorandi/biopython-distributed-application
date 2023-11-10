from Bio import SeqIO, Align
import os
import threading
import multiprocessing
#from numba.openmp import openmp_context as openmp

class Processing:
    def __init__(self, input_file, temp_file, output_file):
        self.input_file = input_file
        self.temp_file = temp_file
        self.output_file = output_file

    def convert_genbank_to_fasta(self):
        sequences = SeqIO.parse(self.input_file, "genbank")
        SeqIO.write(sequences, self.temp_file, "fasta")

    def cleanup_files(self):
        os.remove(self.temp_file)
        os.remove(self.output_file)
        
class Sequential(Processing):
    """ Faz o processamento de dados de modo sequencial """

    def perform_alignment(self):
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
        self.convert_genbank_to_fasta()
        self.perform_alignment()

class Parallel(Processing):
    """ Faz o processamento de dados de modo paralelo """
    
    def __init__(self, input_file, temp_file, output_file, parallel=4):
        super().__init__(input_file, temp_file, output_file)
        self.parallel = parallel

    def convert_genbank_to_fasta(self):
        sequences = SeqIO.parse(self.input_file, "genbank")

        output_files = [f"{self.temp_file}_{i}" for i in range(self.parallel)]
    
        output_handles = [open(file, "w") for file in output_files]
    
        for i, record in enumerate(sequences):
            output_handles[i % self.parallel].write(">" + record.id + "\n" + str(record.seq) + "\n")
            
        for handle in output_handles:
            handle.close()

    def join_files(self):
        file_contents = []

        for i in range(self.parallel):
            with open(f"{self.output_file}_{i}", 'r') as file:
                file_contents.append(file.read())

        joined = "".join(file_contents)

        with open(self.output_file, 'w') as output_file:
            output_file.write(joined)

    def cleanup_files(self):
        for i in range(self.parallel):
            os.remove(f"{self.temp_file}_{i}")

        for i in range(self.parallel):
            os.remove(f"{self.output_file}_{i}")
    
    def perform_alignment(self, i):
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
    """ Faz o processamento de dados utilizando threads """

    def process(self):
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
    """ Faz o processamento de dados utilizando OpenMP """

    def process(self):

        self.convert_genbank_to_fasta()

        #with openmp("parallel"):
        #    with openmp("schedule(static)"):
        #        for i in range(self.parallel):
        #            self.perform_alignment(i)

        self.join_files()
    
class Multiprocess(Parallel):
    """ Faz o processamento de dados utilizando processos """

    def process(self):
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