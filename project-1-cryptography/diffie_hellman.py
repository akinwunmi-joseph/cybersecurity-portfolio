"""
Diffie-Hellman Key Exchange — implemented from scratch.

Demonstrates:
- Discrete logarithm problem (why DH is secure)
- Public/private key exchange over an insecure channel
- Why a passive eavesdropper (MITM) cannot recover the shared secret
  without solving the Discrete Log Problem

No external crypto libraries used.
"""

import random
from rsa_keygen import is_prime, generate_prime


# ── 1. Parameter Generation ───────────────────────────────────────────────────

def find_primitive_root(p: int) -> int:
    """
    Find a primitive root (generator) g modulo p.
    g is a primitive root if {g^1, g^2, ..., g^(p-1)} mod p = {1, 2, ..., p-1}
    """
    if p == 2:
        return 1
    phi = p - 1
    # Factorise phi (p-1) — for a safe prime p=2q+1, factors are just {2, q}
    factors = set()
    n = phi
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)

    for g in range(2, p):
        if all(pow(g, phi // f, p) != 1 for f in factors):
            return g
    raise ValueError("No primitive root found")


def generate_dh_params(bits: int = 256) -> tuple[int, int]:
    """
    Generate a safe prime p and generator g.
    Safe prime: p = 2q + 1, where q is also prime.
    Using small bits here for demo speed; production uses 2048+.
    """
    print(f"[*] Finding a {bits}-bit safe prime p...")
    while True:
        q = generate_prime(bits - 1)
        p = 2 * q + 1
        if is_prime(p):
            break
    g = find_primitive_root(p)
    print(f"[+] p = {p}")
    print(f"[+] g = {g}\n")
    return p, g


# ── 2. Key Exchange ───────────────────────────────────────────────────────────

def dh_generate_private_key(p: int) -> int:
    """Pick a random private key in range [2, p-2]."""
    return random.randint(2, p - 2)


def dh_compute_public_key(g: int, private_key: int, p: int) -> int:
    """Public key = g^private mod p"""
    return pow(g, private_key, p)


def dh_compute_shared_secret(their_public: int, my_private: int, p: int) -> int:
    """Shared secret = their_public^my_private mod p"""
    return pow(their_public, my_private, p)


# ── 3. Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Shared public parameters (sent openly over the network)
    p, g = generate_dh_params(bits=128)  # Small for demo speed

    # Alice generates her keys
    alice_private = dh_generate_private_key(p)
    alice_public  = dh_compute_public_key(g, alice_private, p)
    print(f"[Alice] Private key : {alice_private}")
    print(f"[Alice] Public key  : {alice_public}\n")

    # Bob generates his keys
    bob_private = dh_generate_private_key(p)
    bob_public  = dh_compute_public_key(g, bob_private, p)
    print(f"[Bob]   Private key : {bob_private}")
    print(f"[Bob]   Public key  : {bob_public}\n")

    # They exchange public keys (attacker can see these)
    alice_shared = dh_compute_shared_secret(bob_public,   alice_private, p)
    bob_shared   = dh_compute_shared_secret(alice_public, bob_private,   p)

    print(f"[Alice] Computed shared secret: {alice_shared}")
    print(f"[Bob]   Computed shared secret: {bob_shared}")
    assert alice_shared == bob_shared, "Shared secrets don't match!"
    print("\n[+] Shared secrets match — secure channel established.\n")

    # MITM / Eavesdropper analysis
    print("── Eavesdropper Analysis ───────────────────────────────────────")
    print(f"Attacker can see: p={p}, g={g}")
    print(f"Attacker can see: Alice's public={alice_public}, Bob's public={bob_public}")
    print("To find the shared secret, attacker must solve:")
    print("  alice_public = g^alice_private mod p  →  find alice_private")
    print("This is the Discrete Logarithm Problem — no efficient algorithm exists.")
    print("Eavesdropper attack fails. ✓")
