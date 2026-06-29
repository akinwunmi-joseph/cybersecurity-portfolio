"""
RSA Key Generator — implemented from scratch using number theory.

Demonstrates:
- Prime generation with Miller-Rabin primality test
- Extended Euclidean Algorithm (to find modular inverse)
- RSA key generation (public + private keys)
- Encryption and decryption
- Why a Man-in-the-Middle attack fails against RSA

No external crypto libraries used. Pure math.
"""

import random
import math


# ── 1. Miller-Rabin Primality Test ───────────────────────────────────────────

def is_prime(n: int, rounds: int = 40) -> bool:
    """Probabilistic primality test. False positives < (1/4)^rounds."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)  # Fast modular exponentiation
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int = 512) -> int:
    """Generate a random prime of the given bit length."""
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1  # Odd, correct size
        if is_prime(candidate):
            return candidate


# ── 2. Extended Euclidean Algorithm ──────────────────────────────────────────

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    Used to find the modular multiplicative inverse.
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    return gcd, y1 - (b // a) * x1, x1


def mod_inverse(e: int, phi: int) -> int:
    """Find d such that (e * d) % phi == 1."""
    gcd, x, _ = extended_gcd(e % phi, phi)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist — e and phi(n) must be coprime.")
    return x % phi


# ── 3. RSA Key Generation ─────────────────────────────────────────────────────

def generate_rsa_keys(bits: int = 512):
    """
    Generate an RSA public/private key pair.

    Math recap:
      - Choose two large primes p and q
      - n = p * q  (the modulus)
      - phi(n) = (p-1)(q-1)  (Euler's totient)
      - Choose e coprime to phi(n), typically 65537
      - d = e^-1 mod phi(n)  (private exponent, via Extended GCD)
      - Public key:  (e, n)
      - Private key: (d, n)
    """
    print(f"[*] Generating {bits}-bit primes p and q...")
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    e = 65537  # Standard public exponent — prime, so always coprime to phi(n)
    assert math.gcd(e, phi_n) == 1, "e must be coprime to phi(n)"

    d = mod_inverse(e, phi_n)

    public_key = (e, n)
    private_key = (d, n)

    print(f"[+] Public Key  (e, n): e={e}, n={n}")
    print(f"[+] Private Key (d, n): d={d}\n")

    return public_key, private_key


# ── 4. Encrypt / Decrypt ──────────────────────────────────────────────────────

def rsa_encrypt(message: int, public_key: tuple) -> int:
    """Ciphertext c = m^e mod n"""
    e, n = public_key
    return pow(message, e, n)


def rsa_decrypt(ciphertext: int, private_key: tuple) -> int:
    """Plaintext m = c^d mod n"""
    d, n = private_key
    return pow(ciphertext, d, n)


# ── 5. Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    public_key, private_key = generate_rsa_keys(bits=512)

    # Encrypt a simple integer message (in practice you'd use OAEP padding)
    message = 42
    print(f"[*] Original message : {message}")

    ciphertext = rsa_encrypt(message, public_key)
    print(f"[*] Encrypted        : {ciphertext}")

    decrypted = rsa_decrypt(ciphertext, private_key)
    print(f"[*] Decrypted        : {decrypted}")
    assert decrypted == message, "Decryption failed!"
    print("\n[+] Success — message encrypted and decrypted correctly.\n")

    # MITM demonstration
    print("── Man-in-the-Middle Attack Demo ──────────────────────────────")
    print("Attacker intercepts ciphertext:", ciphertext)
    print("Without the private key d, the attacker must factor n to find d.")
    print(f"n is a {public_key[1].bit_length()}-bit number — computationally infeasible to factor.")
    print("MITM attack fails. ✓")
