# RSA Key Size vs Prime Size Explanation

## Current Implementation: RSA-3072

Our code uses **RSA-3072**, which means:

- **Modulus (n)**: 3072 bits
  - This is the public key component: `n = p × q`
  
- **Each Prime (p and q)**: Approximately **1536 bits each**
  - When you multiply two 1536-bit primes, you get a 3072-bit modulus
  - PyCryptodome automatically generates primes of roughly equal size

## We Do NOT Use 2000-bit Primes

- **2000-bit primes** would create a **~4000-bit modulus** (RSA-4000)
- Our current implementation uses **~1536-bit primes** (RSA-3072)

## Why RSA-3072?

- **Security Level**: ~128 bits of security
- **Performance**: Good balance between security and speed
- **Standard**: Widely recommended for long-term security
- **Prime Size**: ~1536 bits each (sufficiently large and secure)

## If You Want Different Sizes

### For 2000-bit Primes:
- Would need RSA-4000 (approximately)
- Much slower key generation
- Overkill for most use cases

### Current Standard Sizes:
- **RSA-2048**: ~1024-bit primes (112-bit security) - Good
- **RSA-3072**: ~1536-bit primes (128-bit security) - Better ✅ (We use this)
- **RSA-4096**: ~2048-bit primes (156-bit security) - Overkill

## How RSA Works

```
1. Generate two large primes: p and q (each ~1536 bits for RSA-3072)
2. Compute modulus: n = p × q (3072 bits)
3. Compute φ(n) = (p-1) × (q-1)
4. Choose public exponent: e = 65537
5. Compute private exponent: d where e × d ≡ 1 (mod φ(n))
```

The **key size** (3072) refers to the modulus size, not the individual prime size.

## Summary

- ✅ We use **RSA-3072** (3072-bit modulus)
- ✅ Each prime is **~1536 bits** (not 2000 bits)
- ✅ This provides **128-bit security level**
- ✅ This is the **recommended standard** for long-term security

If you specifically need 2000-bit primes, we'd need to change to RSA-4000, but that's generally unnecessary and much slower.

