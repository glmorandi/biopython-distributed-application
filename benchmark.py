import timeit
import csv
import matplotlib.pyplot as plt
from processing.processing import Sequential, OpenMP, Multithread, Multiprocess

num_iter = 1000
num_rep = 5
filename = "benchmark.csv"
results = []

input_file = "ls_orchid.gbk"
temp_file = "temp.fasta"
output_file = "aligned.txt"


def benchmark(method, num_iter, num_rep):
    total_time = 0
    for _ in range(num_rep):
        start_time = timeit.default_timer()
        for _ in range(num_iter):
            method.process()
            method.cleanup_files()
        end_time = timeit.default_timer()
        total_time += (end_time - start_time)
    return total_time / num_rep

seq = Sequential(input_file, temp_file, output_file)

seq_time = benchmark(seq, num_iter, num_rep)
results.append(['Sequential', 1, seq_time])

for cpu in range(1, 17, 2):
    thread = Multithread(input_file, temp_file, output_file, cpu)
    omp = OpenMP(input_file, temp_file, output_file, cpu)
    process = Multiprocess(input_file, temp_file, output_file, cpu)

    thread_time = benchmark(thread, num_iter, num_rep)
    results.append(['Multithread', cpu, thread_time])

    omp_time = benchmark(omp, num_iter, num_rep)
    results.append(['OpenMP', cpu, omp_time])

    process_time = benchmark(process, num_iter, num_rep)
    results.append(['Multiprocess', cpu, process_time])

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(results)


methods = [result[0] for result in results]
cpus = [result[1] for result in results]
speeds = [result[2] for result in results]

plt.figure(figsize=(12, 6))
plt.barh([f'{method} (CPU: {cpu})' for method, cpu in zip(methods, cpus)], speeds)
plt.xlabel('Média do tempo de execução (s)')
plt.ylabel('Método')
plt.title('Resultados')

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig("benchmark.png")

results = sorted(results, key=lambda x: x[2])
results = results[:10]

methods = [result[0] for result in results]
cpus = [result[1] for result in results]
speeds = [result[2] for result in results]

plt.figure(figsize=(12, 6))
plt.barh([f'{method} (CPU: {cpu})' for method, cpu in zip(methods, cpus)], speeds)
plt.xlabel('Média do tempo de execução (s)')
plt.ylabel('Método')
plt.title('Resultados')

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig("top10.png")