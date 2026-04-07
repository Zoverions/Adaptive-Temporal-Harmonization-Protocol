import time
import textwrap

text = "a b a b a b " * 1000

def original():
    tokens = text.split()
    unique_tokens = len(set(tokens))
    total_tokens = len(tokens)
    ratio = unique_tokens / (total_tokens + 1e-5)
    return ratio

def optimized():
    tokens = text.split()
    unique_tokens = len(set(tokens))
    total_tokens = len(tokens)
    ratio = unique_tokens / (total_tokens + 1e-5)
    return ratio

N = 10000

start = time.time()
for _ in range(N):
    original()
end = time.time()
print(f"Original: {end - start:.5f}s")

start = time.time()
for _ in range(N):
    optimized()
end = time.time()
print(f"Optimized: {end - start:.5f}s")
