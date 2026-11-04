import numpy as np
from random import randint
import time

def mat_mul(A, B):
    C = [[0, 0], [0, 0]]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                C[i][j] += A[i][k] * B[k][j]
    return C

def my_gcd(a,b):
  r = a % b
  while r > 0:
    a = b
    b = r
    r = a % b
  return b

def right_power(a,d,m):
    d_list = list(map(int,bin(d)[2:]))
    b = 1
    for i in range(len(d_list)-1, -1, -1):
        if d_list[i] == 1:
            b = (b * a) % m
        a = (a * a) % m
    return b

def mod_inverse(num, mod):
  m = mod
  a = num
  M = [[1,0],[0,1]]
  while m!=0:
    q = a // m
    T =[[0,1],[1,-q]]
    M = mat_mul(M,T)
      
    a, m = m, abs(a) % abs(m) 
  x, y = M[0][0], M[1][0]
  
  res = abs(int(x))
  if num * res % mod == 1:
     return res
  else:
     return mod - res
  

def gen_dm(n,q, max_iter):
    r = 1
    while True:
        p = 2 * r * q + 1
        
        if p <= n:
            r += 1
            continue
            
        found_prime = False
        for _ in range(max_iter):
            a = randint(2, p-1)
            
            if pow(a, p - 1, p) != 1:
                break 
            
            if pow(a, 2 * r, p) != 1:
                return p
        
        r += 1


def rsa_generate_keys(L):
    q, p = 1, 1
    while True:
        i = randint(1,10**(L-1))
        j = randint(1,10**(L-1))
        q = gen_dm(10**(L-1), i,100)
        p = gen_dm(10**(L-1), j,100)
        if q != p and len(str(q)) == L and len(str(p)) == L:
            break
    
    n = p * q
    phi = (p - 1) * (q - 1)
    e = randint(2,phi-1)
    while my_gcd(e,phi) != 1:
        e = randint(2,phi-1)
    
    d = mod_inverse(e,phi)
    return [(e,n),(d,n)]
def rsa_cipher(m,e,n):
    return pow(m,e,n)
def rsa_decipher(c,d,n):
    return pow(c,d,n)

if __name__ == "__main__":
    m = 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890

    
    start_time = time.time()
    e,d = rsa_generate_keys(len(str(m)))
    end_time = time.time()
    print('e = ', e)
    print('e = ', d)
    elapsed_time = end_time - start_time
    print(f"Затраченное время : {elapsed_time:.4f} секунд")
        
    start_time = time.time()
    crypt = rsa_cipher(m,*e)
    end_time = time.time()
    print('crypt = ', crypt)
    elapsed_time = end_time - start_time
    print(f"Затраченное время: {elapsed_time:.4f} секунд")
    
    start_time = time.time()
    decrypt = rsa_decipher(crypt, *d)
    end_time = time.time()
    print('decrypt = ', decrypt)
    elapsed_time = end_time - start_time
    print(f"Затраченное время: {elapsed_time:.4f} секунд")
