import hashlib
import random

def st(n):
    s = 0
    t = n - 1
    while t % 2 == 0:
        s += 1
        t = t // 2
    return s, t
def witness(a,n,s,t):
    
    b = pow(a,t,n)
    if b == 1 or b == n - 1:
        return True
    for _ in range(s-1):
        b = pow(b,2,n) 
        if b == 1:
            return False
        if b == n - 1:
            return True
    return False
def mr(n,k):
    if n % 2 == 0:
        return False
    s,t = st(n)
    for _ in range(k):
        a = random.randint(2,n)
        if not witness(a,n,s,t):
            return False
    return True


def get_prime(nbits):
    low = 2**(nbits - 1)
    high = 2**nbits - 1
    
    while True:
        p = random.randint(low, high)
        if p % 4 == 3 and mr(p, 40):
            return p

        
def generate_keys(L):
    p = get_prime(L // 2)
    q = get_prime(L // 2)
    return (p, q), p * q

def sign(msg, p, q):
    n = p * q
    i = 0
    while True:
        salt = str(i)
        h_val = int(hashlib.sha256((msg + salt).encode()).hexdigest(), 16) % n
        if pow(h_val, (p-1)//2, p) == 1 and pow(h_val, (q-1)//2, q) == 1:
            s_p = pow(h_val, (p+1)//4, p)
            s_q = pow(h_val, (q+1)//4, q)
            s = (s_p * q * pow(q, p-2, p) + s_q * p * pow(p, q-2, q)) % n
            return salt, s
        i += 1

def verify(msg, sig, n):
    salt, s = sig
    h_val = int(hashlib.sha256((msg + salt).encode()).hexdigest(), 16) % n
    return pow(s, 2, n) == h_val

if __name__ == "__main__":

    private_key, public_key = generate_keys(256)
    p, q = private_key
    n = public_key
    print(p,q)
    print(n)


    message = "message"
    signature = sign(message, p, q)


    print(signature)
    print(verify(message, signature, n))
    print(verify('messagaa', signature, n))
