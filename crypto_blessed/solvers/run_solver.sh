#!/bin/bash
# Wrapper script to run solver.py with SageMath environment

export PATH="$HOME/miniforge3/bin:$PATH"
source $HOME/miniforge3/etc/profile.d/conda.sh
conda activate sage

# Install required packages in sage environment if not already installed
pip install -q py_ecc eth-typing pycryptodome pwntools 2>/dev/null || true

# Run the solver
python solver.py
