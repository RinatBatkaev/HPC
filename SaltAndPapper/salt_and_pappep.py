# -*- coding: utf-8 -*-
"""SaltAndPappep.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tvYJZ4dkt_c0U736AjYVOS0FBQWc6TSI
"""

from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from numba import cuda
import numba
import math
from time import time

def add_salt_and_pepper(gb, prob):
  rnd = np.random.rand(gb.shape[0], gb.shape[1])
  noisy = gb.copy()
  noisy[rnd < prob] = 0
  noisy[rnd > 1 - prob] = 255
  return noisy

def median_filter(a):
  b = a.copy()
  start = time()
  for i in range(2, len(a) - 1):
    for j in range(2, len(a[i]) - 1):
      t = [
           a[i - 1][j - 1], a[i - 1][j],  a[i - 1][j + 1], 
           a[i][j - 1],   a[i][j],    a[i][j + 1], 
           a[i + 1][j - 1], a[i + 1][j],  a[i + 1][j + 1]
           ]
      for k in range(8):
        for l in range(8 - k):
          if t[l] > t[l + 1]:
            t[l], t[l + 1] = t[l + 1], t[l]
      b[i][j] = t[int(len(t) / 2)]
  return b, time() - start

@cuda.jit
def gpu_median_filter(a, b):
  i, j = cuda.grid(2)
  t=cuda.local.array(shape=9, dtype=numba.int64)
  t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8] = a[i - 1][j - 1], a[i - 1][j], a[i - 1][j + 1], a[i][j - 1], a[i][j], a[i][j + 1], a[i + 1][j - 1], a[i + 1][j], a[i + 1][j + 1]
  for k in range(8):
    for l in range(8 - k):
      if t[l] > t[l + 1]:
        t[l], t[l + 1] = t[l + 1], t[l]
  b[i][j] = t[int(len(t) / 2)]
    
def prepare_and_exec_gpu(a):
  b = a.copy()
  tread_number_block = 32

  a_global = cuda.to_device(a)
  b_global = cuda.to_device(b)
    
  threadsperblock = (tread_number_block, tread_number_block)
  blockspergrid_x = int(math.ceil(a.shape[0] / threadsperblock[1]))
  blockspergrid_y = int(math.ceil(b.shape[1] / threadsperblock[0]))
  blockspergrid = (blockspergrid_x, blockspergrid_y)

  start = time()
  gpu_median_filter[blockspergrid, threadsperblock](a_global, b_global)
  return b_global.copy_to_host(), time() - start 


img=(Image.open("hd.jpg")).convert('L')
display(img)
img = np.array(img)
n = len(img) * len(img[0])
print('Количество элементов:', n)

img = add_salt_and_pepper(img, 0.09)
display(Image.fromarray(np.uint8(img)))

img2, ctime = median_filter(img)
print('Время на cpu:', ctime)
display(Image.fromarray(np.uint8(img2)))

img2, gtime = prepare_and_exec_gpu(img)
print('Время на gpu:', gtime)
display(Image.fromarray(np.uint8(img2)))