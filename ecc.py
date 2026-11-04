import random

def st(n):
    s, t = 0, n - 1
    while t % 2 == 0:
        s += 1
        t //= 2
    return s, t

def shanks(a, p):
    a %= p
    if a == 0:
        return (0, 0)
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    s, t = st(p)
    while True:
        n = random.randint(1, p - 1)
        if pow(n, (p - 1) // 2, p) == p - 1:
            break
    b = pow(n, t, p)
    r = pow(a, (t + 1) // 2, p)
    d, f = 0, pow(a, t, p)
    for i in range(s):
        if pow(f, pow(2, s - 1 - i), p) != 1:
            d += 2 ** i
            f = (f * pow(b, 2 ** i, p)) % p
    root = (r * pow(b, d // 2, p)) % p
    return (root, p - root)


class Curve:
    def __init__(self, a, b, p):
        self.a, self.b, self.p = a, b, p
        self.pts = []
    def find_points_bf(self):
        pts = [Point(None, None, self)]
        for x in range(self.p):
            rhs = (x**3 + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y**2) % self.p == rhs: 
                    pts.append(Point(x, y, self))
        self.pts = pts
        return pts
    
    def find_points_ts(self):
        pts = [Point(None, None, self)]
        for x in range(self.p):
            rhs = (x**3 + self.a * x + self.b) % self.p
            res = shanks(rhs, self.p)
            if res is not None:
                y1, y2 = res
                pts.append(Point(x, y1, self))
                if y1 != y2: 
                    pts.append(Point(x, y2, self))
        self.pts = pts
        return pts
    
    def get_order(self): 
        return len(self.pts)

    def get_random_point(self): 
        while True:
            x = random.randint(0, self.p - 1)
            rhs = (x**3 + self.a * x + self.b) % self.p
            res = shanks(rhs, self.p)
            if res is not None:
                y = res[0]    
                return Point(x, y, self)


class Point:
    def __init__(self, x, y, curve):
        self.x, self.y, self.curve = x, y, curve
    def __repr__(self):
        return f'<({self.x}, {self.y})>'
    def __neg__(self):
        if self.x is None: return self
        return Point(self.x, (-self.y) % self.curve.p, self.curve)

    def __add__(self, other):
        if self.x is None: 
            return other
        if other.x is None: 
            return self
        p, a = self.curve.p, self.curve.a
        if self.x == other.x and (self.y != other.y or self.y == 0): 
            return Point(None, None, self.curve)
        
        if self.x != other.x:
            k = (other.y - self.y) * pow(other.x - self.x, -1, p)
        else:
            k = (3 * self.x**2 + a) * pow(2 * self.y, -1, p)
        
        k %= p
        x = (k**2 - self.x - other.x) % p
        y = (k * (self.x - x) - self.y) % p
        return Point(x, y, self.curve)

    def __sub__(self, other): 
        return self + (- other)
    def __eq__(self,other):
        return self.x == other.x and self.y == other.y
    
    def __mul__(self, n):
        res = Point(None, None, self.curve)
        q = self
        while n > 0:
            if n % 2: 
                res = res + q
            q = q + q 
            n //= 2
        return res

if __name__ == "__main__":
    crv = Curve(-1, 1, 5)          # y^2 = x^3 − x + 1 (mod 5)
    pts = crv.find_points_bf()

    print(pts)
    print(crv.get_order())

    P, Q = pts[1], pts[3]
    print(f"{P} + {Q} = {P + Q}")
    print(f"{P} + {Q} − {P} = {(P + Q) - P}")    

    for k in range(9):
        print(f"{k}·P = {P * k}")