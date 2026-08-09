# Portfolio status and scope

Evidence snapshot: `62fffee077db702f82dd8d0c14a1c295a5baa856` (2026-08-09 review)

## Current status

This repository is a research-prototype UI and component source under narrowing review. Its recorded default-branch baseline did not pass, and no capability or performance claim has been marked verified. It is not a production policy engine and does not prove moral or ethical correctness.

## Proposed focused boundary

The candidate long-term boundary is a small `ironagent-gca` or `gca-core` policy-heuristic module containing only deterministic, testable routing or scoring behavior. “Moral vectors,” geometric conscience terms, and related outputs must be described as configurable heuristics, not objective measurements.

Do not move into the core module:

- AI Studio/demo shell and presentation-only components;
- unsupported ethical guarantees or metaphysical claims;
- model-generated explanations presented as policy approval;
- duplicated gateway or orchestration behavior already owned by IronAgent or ZovsIronClaw.

## Evidence gates

Before a migration is proposed:

1. Select an explicit code/content license; no reuse grant was detected at the snapshot.
2. Define inputs, outputs, failure states, and risk classes.
3. Add deterministic fixtures for timeout, malformed response, unavailable model, and policy exception.
4. Benchmark routing accuracy, latency, and failure behavior against a declared corpus.
5. Prove high-risk actions fail closed and keep low-risk read-only degradation configurable.
6. Bind every moved file to its source commit and SHA-256 digest.
7. Run destination tests in IronAgent and obtain separate merge approval.

The current Vite configuration injects the Gemini credential into client-side code. Use only a restricted local-evaluation key; a server-side, least-privilege credential boundary and abuse controls are required before any deployment.

Until those gates pass, retain this repository as a preserved prototype and do not advertise it as a validated ethics system.
