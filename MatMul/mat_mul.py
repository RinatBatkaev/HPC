# -*- coding: utf-8 -*-
"""MatMul.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19c2OlmaJCh8Mo93uHc9Xumk8AU2XO18q
"""

!pip3 install pycuda

import numpy as np
import time
import pycuda.autoinit
from pycuda.compiler import SourceModule
from pycuda import gpuarray
import pycuda.driver as drv

import time
import matplotlib.pyplot as plt


mod_multiply = SourceModule("""
    __global__ void multiplyMatrix(int n, float *a, float *b, float *c)
    {
        float c_matrix = 0.f;
        for (int i = 0; i < n; i++)
        {
            float a_matrix = a[threadIdx.y * n + i];
            float b_matrix = b[i * n + threadIdx.x];
            c_matrix += a_matrix * b_matrix;
        }
      
        c[threadIdx.y * n + threadIdx.x] = c_matrix;
    }
""")


def main():
    cpu_time = []
    gpu_time = []

    for N in [i for i in range(100, 2101, 400)]:
        A = np.random.randn(N, N).astype(np.float32)
        B = np.random.randn(N, N).astype(np.float32)

        time_start = time.time()
        cpu_result = np.dot(A,B)
        cpu_time.append(time.time() - time_start)

        a = gpuarray.to_gpu(A)
        b = gpuarray.to_gpu(B)
        c = gpuarray.empty((N, N), np.float32)

        time_start = time.time()
        multiply_matrix = mod_multiply.get_function("multiplyMatrix")
        multiply_matrix(np.uint32(N), a, b, c, block=(16, 16, 1))
        gpu_time.append(time.time() - time_start)

    print(["N", "CPU", "GPU"])
    for i, n in enumerate([i for i in range(100, 2101, 400)]):
        print([n, cpu_time[i], gpu_time[i]])

    plt.plot([i for i in range(100, 2101, 400)], cpu_time, "-b", label="Время вычисления CPU")
    plt.plot([i for i in range(100, 2101, 400)], gpu_time, "-g", label="Время вычисления GPU")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()