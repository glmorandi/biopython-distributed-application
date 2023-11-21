# biopython-processing
  
## Installation

1. **Install Miniconda**

   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

2. **Create a Virtual Environment**
   ```bash
   conda create --name openmp python=3.9
   conda activate openmp
   ```

3. **Install Dependencies**

   Install the project's Python dependencies using pip:

   ```bash
   conda install Python-for-HPC::numba Python-for-HPC::llvmlite -c conda-forge --override-channels
   conda install matplotlib biopython
   ```
   
You can also opt to now use OpenMP and instead use the ``requirements.txt`` with a Python virtual environment.

## Running the Project
1. **Download the dataset**

* https://github.com/biopython/biopython/blob/master/Doc/examples/ls_orchid.gbk

3. **Start the Server**

   Run the server by executing the following command:

   ```bash
   python server/server.py
   ```

4. **Start the Client**

   Run the client by executing the following command:

   ```bash
   python client/client.py
   ```
