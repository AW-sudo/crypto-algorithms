from sympy import factorint
from sympy import randprime
from random import randint
import time

def is_gen(a,p):
    n = p - 1
    Q = factorint(n)
    for q in Q:
        if pow(a, n // q, p) == 1:
            return False
    return True
def rand_gen(p):
    while True:
        a = randint(2, p - 1)
        if is_gen(a, p):
            return a


def gen_keys(N):
    p = randprime(N,10 * N)
    g = rand_gen(p)
    x = randint(2, p - 2)
    y = pow(g, x, p)
    return (y, g, p), x

def cipher(m, e):
    y, g, p = e

    k = randint(2, p - 2)
    a = pow(g, k, p)
    b = (pow(y, k, p) * m) % p
    return (a, b)

def decipher(c, e, x):
    a, b = c
    y, g, p = e
    m = (b * pow(a, p - 1 - x, p)) % p
    return m

if __name__ == "__main__":
    m = 12345678901234567890123456789012345678901234567890123456789012345678901234567890

    start_time = time.time()

    e,d = gen_keys(10**len(str(m)))
    print(e,d)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Затраченное время: {elapsed_time:.4f} секунд")
    start_time = time.time()

    crypt = cipher(m, e)
    print(crypt)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Затраченное время: {elapsed_time:.4f} секунд")
    start_time = time.time()

    decrypt = decipher(crypt,e,d)
    print(decrypt)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Затраченное время: {elapsed_time:.4f} секунд")
