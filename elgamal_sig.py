import sympy
import random
import hashlib

def gen_keys(L):
    found_p = False
    while not found_p:
        q = sympy.randprime(2**(L-2), 2**(L-1))
        p = 2 * q + 1
        if sympy.isprime(p):
            found_p = True

    g = 4 
    x = random.randint(1,p - 3) + 2
    y = pow(g, x, p)

    ke = (y, g, p)
    kd = x
    return ke, kd

def sign(m, ke, kd, hash_algo='sha3_256'):
    y, g, p = ke
    x = kd
    h_hex = hashlib.new(hash_algo, m.encode('utf-8')).hexdigest()
    h = int(h_hex, 16) % (p - 1) 

    while True:
        k = random.randint(2, p - 2)
        if sympy.gcd(k, p - 1) == 1:
            break

    a = pow(g, k, p)

    k_inv = sympy.mod_inverse(k, p - 1)
    b = (k_inv * (h - x * a)) % (p - 1)

    
    return (a, b)
def verify(m, s, ke, hash_algo='sha3_256'):
    y, g, p = ke
    a, b = s

    h_hex = hashlib.new(hash_algo, m.encode('utf-8')).hexdigest()
    h = int(h_hex, 16) % (p - 1)

    if not (0 < a < p):
        return False
    
    left_side = (pow(y, a, p) * pow(a, b, p)) % p
    right_side = pow(g, h, p)

    return left_side == right_side

if __name__ == "__main__":

    ke_A, kd_A = gen_keys(32)
    ke_B, kd_B = gen_keys(32)

    msg = "elgamal-signature"
    wrong_msg = "schnorr-signature"
    sig = sign(msg, ke_A, kd_A)
    print(sig)
    print(verify(msg, sig, ke_A))
    print(verify(wrong_msg, sig, ke_A))
    print(verify(msg, sig, ke_B))

    print("Existential forgery attack")
    def attack_existential(ke):
        y, g, p = ke
        k = random.randint(2, p - 2)
        a = (y * pow(g, k, p)) % p
        b = (-a) % (p - 1)
        m_fake = (-a * k) % (p - 1)
        
        return m_fake, (a, b)

    def verify_no_hash(m, s, ke):
        y, g, p = ke
        a, b = s
        left = (pow(y, a, p) * pow(a, b, p)) % p
        right = pow(g, m, p)
        return left == right

    ke, kd = gen_keys(256)
    y,g,p = ke
    x = kd
    k = random.randint(2,p-2)
    a = y*pow(g,k,p) % p
    b = (- a) % (p-1)
    mfake = (-a*k)% (p-1)
    print('mfake = ', mfake)
    lhs = pow(y,a,p) * pow(a,b,p) % p
    rhs = pow(g,mfake,p)
    print("lhs = rhs ->",lhs == rhs)

    print(ke)
    print(kd)
    m_fake, sig_fake = attack_existential(ke)
    print(m_fake)
    print(sig_fake)
    print("проверка без хеша: ",verify_no_hash(m_fake, sig_fake, ke)) 
    print("проверка с хешем:",verify(str(m_fake),sig_fake,ke))