# Verifiable ZK Clinical Audit Trail

This repository provides a **demonstration of rule-based task classification and an in-memory HMAC-SHA256 audit chain**. Despite its historical name, it does **not** currently implement zero-knowledge proofs, Merkle tree inclusion proofs, patient access authorization, persistent append-only storage, or certified HIPAA/NIST compliance. It must not be used to make clinical decisions or store identifiable patient information.

## What works

- Three deterministic Python workers classify synthetic tasks using a primary metric threshold of **25**, a secondary metric threshold of **12**, a critical flag, and descriptor keywords.
- A supervisor aggregates alerts into a dossier and records hashed task metadata in an in-memory HMAC-SHA256 chain.
- Verification recomputes record HMACs and validates predecessor links. It detects in-memory changes to existing entries, but **cannot detect a truncated history after process restart**, verify original clinical content, or attest the chain without an external trust anchor.
- A CLI supports individual evaluations, CSV batch jobs, status queries, and audit verification. A FastAPI service supports audit and chat endpoints plus metrics.
- `web/index.html` is a self-contained **JavaScript-only demonstration** of the alert classification rules; it does not connect to FastAPI or create cryptographic evidence. The `.github/workflows/pages.yml` workflow publishes this page when GitHub Pages is enabled.

## Browser demonstration

Open `web/index.html` in a current desktop or mobile browser, or use the GitHub Pages deployment if available. Enter **only synthetic examples**, select **Evaluate**, and optionally export local demonstration results as JSON. Results exist only in the current tab's memory and are cleared on refresh; there are no external APIs, trackers, or fonts. The page does not require Pyodide, Python, or network access.

## Local Python usage

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[api,test]"
verifiable-zk-clinical-audit-trail audit --task-id DEMO-001 --target SYNTHETIC --primary 28.5 --secondary 14.2 --status DISCORDANT
verifiable-zk-clinical-audit-trail batch -i sample.csv -o results.csv
verifiable-zk-clinical-audit-trail verify-audit
python -m pytest -q
```

The alternate `zk_audit_trail` Python package is retained for compatibility. It provides a separate threshold evaluator, **not** cryptographic ZK proof generation.

## API and configuration

Start the API with `verifiable-zk-clinical-audit-trail serve` (defaults to localhost, port 8000). For a stable signing key, set `AUDIT_SECRET_KEY` to a randomly generated secret stored outside the repository. Without one, the application warns and uses an **ephemeral random key**; prior chain state is not preserved across processes.

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export AUDIT_READ_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
verifiable-zk-clinical-audit-trail serve
```

- `POST /api/audit`: classify a task and add hashed metadata to the process-local chain.
- `POST /api/chat`: deterministic mock response; no remote language model is contacted.
- `GET /health`, `GET /metrics`: service status and operational counts.
- `GET /api/audit/logs`: disabled unless `AUDIT_READ_TOKEN` is configured; requires `Authorization: Bearer <token>`.

**Privacy and security limits:** Regex filtering catches some common identifiers but is not a comprehensive de-identification method. Avoid raw clinical data. API requests and responses can contain supplied target IDs, and the audit chain is not durable. Do not expose the FastAPI application directly to the public internet without access control, TLS, storage, threat modeling, and further security review.

## Container and CI

The `Dockerfile` installs the declared `[api]` dependencies. `docker compose up --build` requires `AUDIT_SECRET_KEY`; Compose publishes the API only to `127.0.0.1:8000`. GitHub Actions checks Python package installation, compile checks, browser JavaScript syntax, CLI smoke tests, and pytest on supported Python versions.

## License

MIT, as specified in [LICENSE](LICENSE).
