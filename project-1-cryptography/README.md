# Project 1: Cryptographic Tool 🔐

> **The "Math Flex"** — proving I understand the underlying number theory of encryption, not just how to call a library.

## What This Implements

### `rsa_keygen.py` — RSA from Scratch
Full RSA key generation and encryption/decryption built on pure number theory:

| Component | Math Concept |
|-----------|-------------|
| `is_prime()` | Miller-Rabin probabilistic primality test |
| `extended_gcd()` | Extended Euclidean Algorithm |
| `mod_inverse()` | Modular multiplicative inverse |
| `generate_rsa_keys()` | Full RSA key pair generation |

### `diffie_hellman.py` — Diffie-Hellman Key Exchange
Secure key exchange over an insecure channel, built on the Discrete Logarithm Problem.

---

## The Number Theory

### RSA
1. Pick two large primes **p** and **q**
2. Compute **n = p × q** (the modulus)
3. Compute **φ(n) = (p−1)(q−1)** (Euler's totient — counts integers coprime to n)
4. Choose **e** coprime to φ(n) — standard choice is **65537** (prime, fast to compute with)
5. Find **d = e⁻¹ mod φ(n)** using the Extended Euclidean Algorithm
6. **Public key**: (e, n) — share freely
7. **Private key**: (d, n) — keep secret

Encrypt: `c = mᵉ mod n`  
Decrypt: `m = cᵈ mod n`

### Why MITM Fails Against RSA
An attacker intercepting the ciphertext `c` needs `d` to decrypt it. Finding `d` requires knowing `φ(n)`, which requires factoring `n` back into `p` and `q`. **Integer factorisation of a 2048-bit number has no known polynomial-time algorithm** — the best known (General Number Field Sieve) would take longer than the age of the universe on classical hardware.

### Diffie-Hellman & The Discrete Log Problem
Both parties agree on public parameters `(p, g)`. Each picks a secret exponent. The shared secret `g^(ab) mod p` can only be computed by someone who knows `a` or `b`. An eavesdropper seeing `g^a mod p` and `g^b mod p` would need to solve:

```
Find x such that gˣ ≡ A (mod p)
```

This is the **Discrete Logarithm Problem** — also believed to have no efficient classical solution.

---

## How to Run

```bash
# No dependencies — pure Python stdlib
python rsa_keygen.py
python diffie_hellman.py
```

---

## Key Learning
The security of both systems rests not on keeping the algorithm secret (Kerckhoffs's principle) but on the **computational hardness of mathematical problems** — factoring large integers and computing discrete logarithms.
