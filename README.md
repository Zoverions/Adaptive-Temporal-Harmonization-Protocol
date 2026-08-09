<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Adaptive Temporal Harmonization Protocol

> **Status:** Research-prototype UI under scope and evidence review. It is not a validated ethics system or production policy engine. See [`PORTFOLIO_STATUS.md`](PORTFOLIO_STATUS.md).

This repository contains an AI Studio application that can be run locally for evaluation.

View your app in AI Studio: https://ai.studio/apps/drive/1J4ywGH5oZ0jKZ7nE8aPQFOxnbFaEivSg

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Copy [`.env.example`](.env.example) to `.env.local` and set `GEMINI_API_KEY` for local evaluation only. The current Vite configuration exposes the value to browser code; do not use a production or broadly scoped credential. A server-side proxy is required before deployment.
3. Run the app:
   `npm run dev`
