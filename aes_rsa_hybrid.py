import numpy as np
import sympy as sp
from functools import reduce
from operator import xor
from random import randint

x = sp.Symbol('x')
AES_POLY = sp.Poly(x**8 + x**4 + x**3 + x**2 + 1, x, domain=sp.GF(2))
class GF28Element:
    def __init__(self, value):
        if isinstance(value, (int, np.integer)):
            coeffs = [int(b) for b in f"{int(value):08b}"]
            self.poly = sp.Poly.from_list(coeffs, gens=x, domain=sp.GF(2))
        elif isinstance(value, (list, tuple, np.ndarray)):
            self.poly = sp.Poly.from_list(list(value), gens=x, domain=sp.GF(2))
        elif isinstance(value, sp.Poly):
            self.poly = value.set_domain(sp.GF(2))
        elif isinstance(value, GF28Element):
            self.poly = value.poly
        else:
            self.poly = sp.Poly(0, x, domain=sp.GF(2))
        
        if self.poly.degree() >= 8:
            self.poly = sp.rem(self.poly, AES_POLY, domain=sp.GF(2))

    def to_int(self) -> int:
        if self.poly.is_zero:
            return 0
        coeffs = self.poly.all_coeffs()
        return sum(int(c) * (2 ** i) for i, c in enumerate(reversed(coeffs)))

    def __add__(self, other):
        return GF28Element(self.poly + GF28Element(other).poly)

    __sub__ = __add__  
    __radd__ = __add__

    def __mul__(self, other):
        return GF28Element(self.poly * GF28Element(other).poly)
    
    __rmul__ = __mul__

    def inverse(self):
        if self.to_int() == 0:
            return GF28Element(0)
        s, t, gcd = sp.gcdex(self.poly, AES_POLY)
        return GF28Element(s % AES_POLY)

    def __eq__(self, other):
        return self.to_int() == GF28Element(other).to_int()

    def __repr__(self):
        return f'{self.poly}'

def vector_to_state(vector):
    state = [[None for _ in range(4)] for _ in range(4)]
    for i, val in enumerate(vector):
        row = i % 4
        col = i // 4
        state[row][col] = GF28Element(val)
    return state

def state_to_vector(state):
    vector = [0] * 16
    for col in range(4):
        for row in range(4):
            vector[col * 4 + row] = state[row][col].to_int()
    return vector

def build_sbox():
    row = [1, 0, 0, 0, 1, 1, 1, 1] 
    A = np.array([np.roll(row, i) for i in range(8)])
    v = np.array([1, 1, 0, 0, 0, 1, 1, 0]) # 0x63
    sbox = []
    for val in range(256):
        inv_val = GF28Element(val).inverse().to_int()
        b = np.unpackbits(np.array([inv_val], dtype=np.uint8), bitorder='little')
        res_bits = (A @ b + v) % 2
        res = np.packbits(res_bits, bitorder='little')[0]
        sbox.append(res)
    return sbox

SBOX = build_sbox()

def build_inv_sbox():
    inv_sbox = [0] * 256
    for i in range(256):
        inv_sbox[SBOX[i]] = i
    return inv_sbox

invSBOX = build_inv_sbox()

base = [0x02, 0x03, 0x01, 0x01]
C_MATRIX = [[GF28Element(base[(j - i) % 4]) for j in range(4)] for i in range(4)]

inv_base = [0x0e, 0x0b, 0x0d, 0x09]
INV_C_MATRIX = [[GF28Element(inv_base[(j - i) % 4]) for j in range(4)] for i in range(4)]

def SubBytes(state):
    for r in range(4):
        for c in range(4):
            val = state[r][c].to_int()
            state[r][c] = GF28Element(SBOX[val])
    return state

def InvSubBytes(state):
    for r in range(4):
        for c in range(4):
            val = state[r][c].to_int()
            state[r][c] = GF28Element(invSBOX[val])
    return state

def ShiftRows(state):
    new_state = []
    for r in range(4):
        shifted_row = state[r][r:] + state[r][:r]
        new_state.append(shifted_row)
    return new_state

def InvShiftRows(state):
    new_state = []
    for r in range(4):
        shifted_row = state[r][-r:] + state[r][:-r] if r > 0 else state[r][:]
        new_state.append(shifted_row)
    return new_state

def MixColumns(state):
    columns = np.transpose(state)
    new_state = []
    for row in C_MATRIX:
        new_row = []
        for col in columns:
            res = reduce(xor, [(r_el * c_el).to_int() for r_el, c_el in zip(row, col)])
            new_row.append(GF28Element(res))
        new_state.append(new_row)
    return new_state

def InvMixColumns(state):
    columns = np.transpose(state)
    new_state = []
    for row in INV_C_MATRIX:
        new_row = []
        for col in columns:
            res = reduce(xor, [(r_el * c_el).to_int() for r_el, c_el in zip(row, col)])
            new_row.append(GF28Element(res))
        new_state.append(new_row)
    return new_state

def AddRoundKey(state, round_key):
    key_state = vector_to_state(round_key)
    new_state = [[None for _ in range(4)] for _ in range(4)]
    for r in range(4):
        for c in range(4):
            val = state[r][c].to_int() ^ key_state[r][c].to_int()
            new_state[r][c] = GF28Element(val)
    return new_state

def print_state(state, hex_format=False):
    if hex_format:
        display_data = np.vectorize(lambda x: f"0x{x.to_int():02x}")(state)
    else:
        display_data = np.vectorize(lambda x: x.poly.as_expr())(state)
    
    print(tabulate(display_data, tablefmt='grid'))


RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

def expand_key_aes256(key_bytes):
    w = [list(key_bytes[4*i : 4*i+4]) for i in range(8)]
    for i in range(8, 60):
        temp = w[i-1][:]
        if i % 8 == 0:
            temp = temp[1:] + temp[:1] # RotWord
            temp = [SBOX[b] for b in temp] # SubWord
            temp[0] ^= RCON[(i//8) - 1] # Rcon
        elif i % 8 == 4:
            temp = [SBOX[b] for b in temp] # SubWord
        
        w.append([w[i-8][j] ^ temp[j] for j in range(4)])
    
    round_keys = []
    for i in range(15):
        round_key = []
        for j in range(4):
            round_key.extend(w[i*4 + j])
        round_keys.append(round_key)
    return round_keys

def AES_block_encrypt(state, round_keys): 

    state = AddRoundKey(state, round_keys[0])
    
    for i in range(1, 14):
        state = SubBytes(state)
        state = ShiftRows(state)
        state = MixColumns(state)
        state = AddRoundKey(state, round_keys[i])
        
    state = SubBytes(state)
    state = ShiftRows(state)
    state = AddRoundKey(state, round_keys[14])
    
    return state

def AES_block_decrypt(state, round_keys):

    state = AddRoundKey(state, round_keys[14])
    
    for i in range(13, 0, -1):
        state = InvShiftRows(state)
        state = InvSubBytes(state)
        state = AddRoundKey(state, round_keys[i])
        state = InvMixColumns(state)

    state = InvShiftRows(state)
    state = InvSubBytes(state)
    state = AddRoundKey(state, round_keys[0])

    return state

def text_to_vectors(text):
    data = text.encode('utf-8')
    padding_len = 16 - (len(data) % 16)
    data += bytes([padding_len] * padding_len) 
    return [list(data[i:i+16]) for i in range(0, len(data), 16)]

def vectors_to_text(vectors):
    all_bytes = []
    for v in vectors:
        all_bytes.extend(v)
    data = bytes(all_bytes)
    padding_len = data[-1]
    if 1 <= padding_len <= 16:
        data = data[:-padding_len]
    return data.decode('utf-8')


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
    dP = d % (p-1)
    dQ = d % (q-1)
    qInv = mod_inverse(q,p)
    return [(e,n),(p,q,dP,dQ,qInv)]

def rsa_cipher(m,e,n):
    return pow(m,e,n)

def rsa_decipher(c,d):
    p,q,dP,dQ,qInv = d
    mp = pow(c,dP,p)
    mq = pow(c,dQ,q)
    y = (mp - mq) * qInv % p
    m = mq + q * y
    return m

def rsa_encrypt_key(aes_key_bytes, pub_key):
    e, n = pub_key
    m = int.from_bytes(aes_key_bytes, 'little')
    return rsa_cipher(m, e, n)

def rsa_decrypt_key(encrypted_key_int, priv_key_tuple):
    m = rsa_decipher(encrypted_key_int, priv_key_tuple)
    return list(int.to_bytes(m,32, 'little'))

if __name__ == "__main__":
    from tabulate import tabulate
    key_256 = np.random.randint(0, 256, 32).tolist()
    round_keys = expand_key_aes256(key_256)
    print(key_256)
    # for rk in round_keys:
    #     print(rk)
    pub, priv = rsa_generate_keys(45)
    print(pub)
    print(priv)
    print(key_256)

    enc_key_int = rsa_encrypt_key(key_256,pub)
    print("ключ aes в rsa", enc_key_int)
    original_text = "Advanced Encryption Standard"
    vectors = text_to_vectors(original_text)
    print(vectors)
    blocks = []
    for v in vectors:
        b = vector_to_state(v)
        blocks.append(b)
        print_state(b,True)

    encrypted_blocks = []
    for block in blocks:
        enc_block = AES_block_encrypt(block, round_keys)
        encrypted_blocks.append(enc_block)
        print_state(enc_block,True)

    priv
    key_256_recv = rsa_decrypt_key(enc_key_int, priv)
    round_keys_recv = expand_key_aes256(key_256_recv)
    print(key_256_recv == key_256)
    decrypted_blocks = []
    for block in encrypted_blocks:
        dec_block = AES_block_decrypt(block, round_keys_recv)
        decrypted_blocks.append(dec_block)
        print_state(dec_block,True)
    dec_vectors = []
    for b in decrypted_blocks:
        dv = state_to_vector(b)
        dec_vectors.append(dv)
        print(dv)
    dec_text = vectors_to_text(dec_vectors)
    print(dec_text)