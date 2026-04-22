import random


def mod_exp(a:int , b:int , c:int) -> int:
    return pow(a,b,c)


def gcd(a:int , b:int) -> int:
    while b != 0:
        a,b = b ,a % b
    return abs(a)

def extended_gcd(a:int , b:int) -> tuple[int,int,int]:
    r_old, r_cur = a, b
    x_old, x_cur = 1, 0
    y_old, y_cur = 0, 1

    while r_cur != 0:
        q = r_old // r_cur 
        r_old, r_cur = r_cur, r_old - q * r_cur
        x_old, x_cur = x_cur, x_old - q * x_cur
        y_old, y_cur = y_cur, y_old - q * y_cur
    return r_old, x_old, y_old

def mod_inverse(a: int, mod: int) -> int:
    g, x, y = extended_gcd(a, mod)
    if g != 1:
        raise ValueError(f"No modular inverse for {a} mod {mod}")
    return x % mod

def random_int(low: int, high: int) -> int:
    if low > high:
        raise ValueError("low cannot be greater than high")
    return random.SystemRandom().randint(low, high)

def is_prime(n:int) -> bool:
    if n < 2:
        return False
    if n in (2,3):
        return True
    if n % 2 == 0:
        return False
    
    i = 3 
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True

def factorize(n: int) -> list[int]:
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n = n // d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

    

def is_primitive_root(alpha:int,p:int) -> bool:
    if p < 3:
        return False
    if alpha <= 1 or alpha >= p:
        return False
    if not is_prime(p):
        return False
    
    phi = p -1 
    prime_factors = factorize(phi)
    for i in prime_factors:
        if mod_exp(alpha, phi // i, p) == 1:
            return False
        
    return True

