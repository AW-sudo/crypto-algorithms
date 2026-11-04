#include <iostream>
#include <vector>
#include <optional>
#include <random>
#include <utility>

using i64 = long long;

static i64 mod_pow(i64 base, i64 exp, i64 mod) {
    i64 result = 1 % mod;
    base = ((base % mod) + mod) % mod;
    while (exp > 0) {
        if (exp & 1) result = (i64)((__int128)result * base % mod);
        base = (i64)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}

static std::pair<int, i64> st(i64 n) {
    int s = 0;
    i64 t = n - 1;
    while (t % 2 == 0) { s++; t /= 2; }
    return {s, t};
}

static std::optional<std::pair<i64, i64>> shanks(i64 a, i64 p) {
    a = ((a % p) + p) % p;
    if (a == 0) return std::make_pair(0LL, 0LL);
    if (mod_pow(a, (p - 1) / 2, p) != 1) return std::nullopt;

    auto [s, t] = st(p);
    std::mt19937_64 rng(std::random_device{}());

    i64 n;
    while (true) {
        n = (i64)(rng() % (unsigned long long)(p - 1)) + 1;
        if (mod_pow(n, (p - 1) / 2, p) == p - 1) break;
    }

    i64 b = mod_pow(n, t, p);
    i64 r = mod_pow(a, (t + 1) / 2, p);
    i64 d = 0;
    i64 f = mod_pow(a, t, p);

    for (int i = 0; i < s; i++) {
        i64 fk = f;
        for (int j = 0; j < s - 1 - i; j++)
            fk = (i64)((__int128)fk * fk % p);
        if (fk != 1) {
            d += (1LL << i);
            f = (i64)((__int128)f * mod_pow(b, 1LL << i, p) % p);
        }
    }

    i64 root = (i64)((__int128)r * mod_pow(b, d / 2, p) % p);
    return std::make_pair(root, (p - root) % p);
}

class Curve;

class Point {
public:
    std::optional<i64> x, y;
    Curve* curve;

    Point(std::optional<i64> x_, std::optional<i64> y_, Curve* c)
        : x(x_), y(y_), curve(c) {}

    Point operator-() const;
    Point operator+(const Point& other) const;
    Point operator-(const Point& other) const;
    bool operator==(const Point& other) const;
    Point operator*(i64 n) const;
};

class Curve {
public:
    i64 a, b, p;
    std::vector<Point> pts;

    Curve(i64 a_, i64 b_, i64 p_) : a(a_), b(b_), p(p_) {}

    std::vector<Point> find_points_bf();
    std::vector<Point> find_points_ts();
    int get_order() const { return (int)pts.size(); }
    Point get_random_point();
};

inline Point Point::operator-() const {
    if (!x.has_value()) return *this;
    i64 m = curve->p;
    return Point(*x, ((-*y) % m + m) % m, curve);
}

inline Point Point::operator+(const Point& other) const {
    if (!x.has_value()) return other;
    if (!other.x.has_value()) return *this;

    i64 p = curve->p, a = curve->a;
    i64 xm = *x, ym = *y, xo = *other.x, yo = *other.y;

    if (xm == xo && (ym != yo || ym == 0))
        return Point(std::nullopt, std::nullopt, curve);

    i64 k;
    if (xm != xo) {
        i64 dy = ((yo - ym) % p + p) % p;
        i64 dx = ((xo - xm) % p + p) % p;
        k = (i64)((__int128)dy * mod_pow(dx, p - 2, p) % p);
    } else {
        i64 num = ((3 * (i64)((__int128)xm * xm % p) + a) % p + p) % p;
        i64 den = ((2 * ym) % p + p) % p;
        k = (i64)((__int128)num * mod_pow(den, p - 2, p) % p);
    }

    i64 xr = (((i64)((__int128)k * k % p) - xm - xo) % p + p) % p;
    i64 yr = (((i64)((__int128)k * (((xm - xr) % p + p) % p) % p) - ym) % p + p) % p;
    return Point(xr, yr, curve);
}

inline Point Point::operator-(const Point& other) const {
    return *this + (-other);
}

inline bool Point::operator==(const Point& other) const {
    return x == other.x && y == other.y;
}

inline Point Point::operator*(i64 n) const {
    Point res(std::nullopt, std::nullopt, curve);
    Point q = *this;
    while (n > 0) {
        if (n & 1) res = res + q;
        q = q + q;
        n >>= 1;
    }
    return res;
}

inline std::vector<Point> Curve::find_points_bf() {
    pts.clear();
    pts.emplace_back(std::nullopt, std::nullopt, this);
    for (i64 x = 0; x < p; x++) {
        i64 x3 = (i64)((__int128)x * x % p * x % p);
        i64 ax = (i64)((__int128)a * x % p);
        i64 rhs = ((x3 + ax + b) % p + p) % p;
        for (i64 y = 0; y < p; y++) {
            if ((i64)((__int128)y * y % p) == rhs)
                pts.emplace_back(x, y, this);
        }
    }
    return pts;
}

inline std::vector<Point> Curve::find_points_ts() {
    pts.clear();
    pts.emplace_back(std::nullopt, std::nullopt, this);
    for (i64 x = 0; x < p; x++) {
        i64 x3 = (i64)((__int128)x * x % p * x % p);
        i64 ax = (i64)((__int128)a * x % p);
        i64 rhs = ((x3 + ax + b) % p + p) % p;
        auto res = shanks(rhs, p);
        if (res.has_value()) {
            auto [y1, y2] = *res;
            pts.emplace_back(x, y1, this);
            if (y1 != y2) pts.emplace_back(x, y2, this);
        }
    }
    return pts;
}

inline Point Curve::get_random_point() {
    std::mt19937_64 rng(std::random_device{}());
    while (true) {
        i64 x = (i64)(rng() % (unsigned long long)p);
        i64 x3 = (i64)((__int128)x * x % p * x % p);
        i64 ax = (i64)((__int128)a * x % p);
        i64 rhs = ((x3 + ax + b) % p + p) % p;
        auto res = shanks(rhs, p);
        if (res.has_value()) return Point(x, res->first, this);
    }
}

std::ostream& operator<<(std::ostream& os, const Point& pt) {
    if (!pt.x.has_value()) os << "<(None, None)>";
    else os << "<(" << *pt.x << ", " << *pt.y << ")>";
    return os;
}

int main() {
    Curve crv(-1, 1, 5);
    auto pts = crv.find_points_bf();

    std::cout << "[";
    for (size_t i = 0; i < pts.size(); i++) {
        if (i) std::cout << ", ";
        std::cout << pts[i];
    }
    std::cout << "]\n";
    std::cout << crv.get_order() << "\n";

    Point P = pts[1], Q = pts[3];
    std::cout << P << " + " << Q << " = " << (P + Q) << "\n";
    std::cout << P << " + " << Q << " - " << P << " = " << ((P + Q) - P) << "\n";

    for (int k = 0; k < 9; k++)
        std::cout << k << "·P = " << (P * k) << "\n";

    return 0;
}