"""Regression tests for audit chain integrity, validation, and protected reads."""
import math
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.api import app


def test_hmac_detects_payload_hash_tampering():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("service", "supervisor", "COMPLETE", {"count": 1})
    trail.log("service", "supervisor", "COMPLETE", {"count": 2})
    assert trail.verify_integrity()
    trail.logs[0]["payload_hash"] = "0" * 64
    assert not trail.verify_integrity()


@pytest.mark.parametrize("field", ["audit_id", "timestamp", "actor", "actor_tier", "event_type", "prev_hash", "current_hash"])
def test_hmac_detects_metadata_tampering(field):
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("service", "supervisor", "COMPLETE", {"count": 1})
    trail.logs[0][field] = "modified"
    assert trail.verify_integrity() is False


def test_readers_cannot_modify_internal_trail():
    trail = AuditTrail(secret_key="test-only-key")
    returned = trail.log("service", "supervisor", "COMPLETE", {"count": 1})
    returned["current_hash"] = "changed"
    copy = trail.get_trail()
    copy[0]["prev_hash"] = "changed"
    assert trail.verify_integrity() is True


def test_no_pii_in_audit_metadata():
    trail = AuditTrail(secret_key="test-only-key")
    with pytest.raises(SecurityException):
        trail.log("patient@example.org", "supervisor", "COMPLETE", {"count": 1})
    assert trail.get_trail() == []


@pytest.mark.parametrize("value", [float("nan"),float("inf"),float("-inf")])
def test_metrics_must_be_finite(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="TASK",target_identifier="PSEUDONYM",primary_metric=value)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="TASK",target_identifier="PSEUDONYM",primary_metric=2,secondary_metric=value)


def test_attributes_are_guarded():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(task_id="TASK",target_identifier="PSEUDONYM",primary_metric=2,attributes={"contact":"person@example.org"})
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_log_endpoint_requires_configured_token(monkeypatch):
    client=TestClient(app)
    monkeypatch.delenv("AUDIT_READ_TOKEN",raising=False)
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("AUDIT_READ_TOKEN","local-test-token")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs",headers={"Authorization":"Bearer incorrect"}).status_code == 403
    response=client.get("/api/audit/logs",headers={"Authorization":"Bearer local-test-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_browser_demo_has_no_fake_signatures():
    from pathlib import Path
    page=(Path(__file__).parents[1]/"web"/"index.html").read_text(encoding="utf-8")
    assert 'cryptographic_proof:null' in page
    assert "HMAC_SHA256_e83f" not in page
    assert "fetch('/api/audit'" not in page
