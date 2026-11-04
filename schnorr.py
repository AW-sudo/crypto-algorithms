import sympy
import random
import hashlib

def generate_keys_schnorr(L, N):
    q = sympy.randprime(2**(N-1), 2**N)
    found_p = False
    while not found_p:
        
        k_min = (2**(L-1)) // q
        k_max = (2**L) // q
        k = random.randint(k_min, k_max)
        
        p = k * q + 1
        if p.bit_length() == L and sympy.isprime(p):
            found_p = True

   
    while True:
        g_tilde = random.randint(2, p - 1)   
        g = pow(g_tilde, (p - 1) // q, p)
        if g != 1:
            break

    x = random.randint(2, q - 1)
    y = pow(g, x, p)

    ke = (y, g, p, q)
    kd = x
    
    return ke, kd

def sign_schnorr(m, ke, kd):
    y, g, p, q = ke
    x = kd
    k = random.randint(2, q - 1)
    a = pow(g, k, p)
    hash_input = str(a) + m
    h_hex = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    h = int(h_hex, 16) % q
    b = (k - x * h) % q
    return (b, h)

def verify_schnorr(m, s, ke):
    y, g, p, q = ke
    b, h = s
    a_prime = (pow(g, b, p) * pow(y, h, p)) % p
    hash_input = str(a_prime) + m
    h_prime_hex = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    h_prime = int(h_prime_hex, 16) % q
    return h == h_prime

def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    ke_A, kd_A = generate_keys_schnorr(512, 160)
    ke_B, _ = generate_keys_schnorr(512, 160)
    msg, wrong_msg = "schnorr_signature", "elgamal_signature"
    sig = sign_schnorr(msg, ke_A, kd_A)

    print(verify_schnorr(msg, sig, ke_A))
    print(verify_schnorr(wrong_msg, sig, ke_A))
    print(verify_schnorr(msg, sig, ke_B))
    print(verify_schnorr(msg, (sig[0]+1, sig[1]), ke_A)) 

    print("Reused Nonce Attack")


    ke, x_true = generate_keys_schnorr(512, 160)
    y, g, p, q = ke
    print(x_true)

    k_fixed = random.randint(2, q - 1) 
    a = pow(g, k_fixed, p)

    m1, m2 = "Сообщезние один", "Сообщение два"


    h1 = int(hashlib.sha256((str(a) + m1).encode()).hexdigest(), 16) % q
    b1 = (k_fixed - x_true * h1) % q
    sig1 = (b1, h1)


    h2 = int(hashlib.sha256((str(a) + m2).encode()).hexdigest(), 16) % q
    b2 = (k_fixed - x_true * h2) % q
    sig2 = (b2, h2)

    print(verify_schnorr(m1, sig1, ke))
    print(verify_schnorr(m2, sig2, ke))


    x_hacked = ((b1 - b2) * sympy.mod_inverse(h2 - h1, q)) % q
    print(x_hacked)
    print(x_true == x_hacked)