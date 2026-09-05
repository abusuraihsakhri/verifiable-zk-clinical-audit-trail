# Verifiable ZK Clinical Audit Trail

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Reference Guidelines & Standards:** `NIST FIPS 203/204/205, NIST SP 800-90B & ISO/IEC Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Verifiable ZK Clinical Audit Trail** is an advanced analytical and computational platform implementing Merkle tree zero-knowledge EHR access inclusion & HIPAA audit trail prover. It provides:

- **Multi-Agent Consensus**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate tasks and produce consensus dossiers.
- **Tamper-Evident Audit Trail**: HMAC-SHA256 chained cryptographic ledger for every evaluation and state transition.
- **Zero-PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers from outbound data.
- **FastAPI REST API**: OpenAPI 3.1 endpoints with Prometheus telemetry (`/metrics`).
- **Enrichment Suite**: Eight domain-specific engines for ZK-SNARK proofs, HIPAA compliance, clinical trial data sharing, and more.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Prometheus Metrics**: Operational telemetry for monitoring task throughput, alert rates, and audit chain growth.

---

## 💻 CLI Quickstart & Usage

### Installation

```bash
pip install -e .
```

### 1. Run Single Audit Task
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task/case identifier | `TASK-2026-001` |
| `--target` | Entity, patient key, or target identifier | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement or score | `28.5` |
| `--secondary` | Secondary kinetic or confidence score | `14.2` |
| `--critical` | Emergency escalation flag | `False` |
| `--status` | Status code or phenotype descriptor | `DISCORDANT` |

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or target identifier | Required |
| `primary_metric` | Primary domain measurement | Required |
| `secondary_metric` | Secondary kinetic score | Optional (default: 5.0) |
| `is_critical_flag` | Emergency escalation flag | Optional (default: False) |
| `status_descriptor` | Status code or phenotype | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable to a strong random value in production:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((1..32 | ForEach-Object { Get-Random -Max 16 }).ForEach({ "{0:x}" -f $_ }))
```

**Warning:** If `AUDIT_SECRET_KEY` is not set, the system will emit a runtime warning and use an insecure default. Never run in production without setting this variable.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t verifiable-zk-clinical-audit-trail .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key verifiable-zk-clinical-audit-trail
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker-compose up -d
```

---

## 📁 Project Structure

```
verifiable-zk-clinical-audit-trail/
├── agents/                    # Core multi-agent system
│   ├── __init__.py           # Package version
│   ├── api.py                # FastAPI REST server
│   ├── base.py               # Security, PHI guard, HMAC audit trail
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM provider factory
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data models
│   ├── streamer.py           # WebSocket telemetry broadcaster
│   ├── supervisor.py         # Master orchestrator
│   └── workers.py            # Specialized domain workers
├── zk_audit_trail/           # ZK-AuditTrail sub-package
│   ├── __init__.py
│   ├── agents.py             # Merkle tree & ZK proof agents
│   ├── cli.py                # CLI for ZK-AuditTrail
│   ├── engine.py             # Core algorithmic engine
│   ├── models.py             # Data models
│   └── server.py             # FastAPI server factory
├── tests/                    # Pytest test suite
│   ├── test_verifiable_zk_clinical_audit_trail.py
│   ├── test_enrichment.py
│   └── test_zk_audit_trail.py
├── cli.py                    # Main CLI entry point
├── enrichment.py             # Domain enrichment engines
├── simulator.py              # High-throughput stress tester
├── sample.csv                # Sample batch input
├── sample_payload.json       # Sample API payload
├── benchmark_dataset.json    # Golden benchmark test cases
├── openapi_spec.json         # OpenAPI 3.1 specification
├── Dockerfile                # Container build config
├── docker-compose.yml        # Multi-container orchestration
├── pyproject.toml            # Python package metadata
└── README.md                 # This file
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
