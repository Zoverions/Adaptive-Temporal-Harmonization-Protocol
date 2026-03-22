### Optimization Rationale: Batch Decoding in HuggingFace Tokenizers

**Current Implementation:**
The current `auto_tune` and `auto_tune_strength` methods in `gca_core/optimizer.py` and `gca_optimizer.py` respectively, decode each generated sequence from a batch one by one using `tokenizer.decode()` inside a loop.

**The Problem:**
HuggingFace's `PreTrainedTokenizer` (and its "Fast" variants) is highly optimized for batch operations. Calling `decode()` individually incurs repeated overhead for setting up the decoding environment, handling special tokens, and managing internal state for each item.

**The Optimization:**
By using `tokenizer.batch_decode()`, we can process all sequences in the batch in a single call. This allows the tokenizer to:
1.  **Parallelize Decoding:** Fast tokenizers (written in Rust) can often parallelize decoding across multiple threads when given a batch.
2.  **Reduce Python Overhead:** It minimizes the number of calls from Python to the underlying tokenizer implementation (C++ or Rust), reducing overhead.
3.  **Optimize Memory Handling:** It enables the tokenizer to manage memory more efficiently by allocating buffers for the entire batch at once.

**Project Impact:**
While full end-to-end performance measurements are constrained by the current environment, `batch_decode` is widely recognized as the standard best practice for performance when dealing with batches of tokenized sequences. This change improves the efficiency of the auto-tuning process, making the agent more responsive during skill matching and optimization.
