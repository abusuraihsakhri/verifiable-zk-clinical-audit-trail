"""
Security and input validation tests for verifiable-zk-clinical-audit-trail.
"""
import sys
import os
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload
from enrichment import BaseEnrichmentEngine, FeaturesEngine, VerifiablezkclinicalaudittrailEnrichmentSuite


class TestAuditTrailSecurity:
    """Tests for HMAC audit trail security configuration."""

    def test_audit_trail_warns_on_missing_secret_key(self):
        """AuditTrail should warn when AUDIT_SECRET_KEY is not set."""
        original_key = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                trail = AuditTrail()
                assert len(w) == 1
                assert "AUDIT_SECRET_KEY not set" in str(w[0].message)
                assert issubclass(w[0].category, RuntimeWarning)
        finally:
            if original_key is not None:
                os.environ["AUDIT_SECRET_KEY"] = original_key

    def test_audit_trail_uses_env_var_when_set(self):
        """AuditTrail should use AUDIT_SECRET_KEY from environment."""
        os.environ["AUDIT_SECRET_KEY"] = "test-secret-key-12345"
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                trail = AuditTrail()
                # Should not warn when env var is set
                security_warnings = [x for x in w if "AUDIT_SECRET_KEY" in str(x.message)]
                assert len(security_warnings) == 0
        finally:
            os.environ.pop("AUDIT_SECRET_KEY", None)

    def test_audit_trail_uses_explicit_key(self):
        """AuditTrail should use explicitly provided key."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail(secret_key="explicit-test-key")
            security_warnings = [x for x in w if "AUDIT_SECRET_KEY" in str(x.message)]
            assert len(security_warnings) == 0
            assert trail.secret_key == b"explicit-test-key"

    def test_audit_trail_integrity_verification(self):
        """Audit trail should maintain cryptographic integrity."""
        trail = AuditTrail(secret_key="test-key")
        trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 2


class TestPHIGuard:
    """Tests for PHI outbound guard patterns."""

    def test_phi_guard_blocks_mrn(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Patient MRN-12345678")

    def test_phi_guard_blocks_ssn(self):
        with pytest.raises(SecurityException):
            assert_no_phi("SSN: 123-45-6789")

    def test_phi_guard_blocks_phone(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Call 555-123-4567")

    def test_phi_guard_blocks_email(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Email: patient@example.com")

    def test_phi_guard_allows_clean_text(self):
        """Clean analytical text should pass without exception."""
        assert_no_phi("Analytical assay specimen KEY-001 optimal") is None

    def test_phi_guard_handles_empty_string(self):
        """Empty string should pass without exception."""
        assert_no_phi("") is None

    def test_phi_redaction(self):
        """PHIGuard should redact sensitive patterns."""
        redacted = PHIGuard.redact_phi("Patient MRN-12345678 and SSN 123-45-6789")
        assert "MRN" not in redacted or "[REDACTED_IDENTIFIER]" in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted


class TestEnrichmentEngineBase:
    """Tests for the refactored base enrichment engine."""

    def test_base_engine_optimal(self):
        engine = FeaturesEngine(threshold=1.0)
        result = engine.evaluate(0.5)
        assert result.status == "OPTIMAL"
        assert len(result.alerts) == 0

    def test_base_engine_warning(self):
        engine = FeaturesEngine(threshold=1.0)
        result = engine.evaluate(1.5)
        assert result.status == "WARNING"
        assert len(result.alerts) == 1

    def test_base_engine_critical(self):
        engine = FeaturesEngine(threshold=1.0)
        result = engine.evaluate(3.0)
        assert result.status == "CRITICAL_ALERT"
        assert len(result.alerts) == 1

    def test_base_engine_history_tracking(self):
        engine = FeaturesEngine(threshold=1.0)
        engine.evaluate(0.5)
        engine.evaluate(1.5)
        engine.evaluate(3.0)
        assert len(engine.history) == 3

    def test_base_engine_feature_name(self):
        engine = FeaturesEngine()
        assert engine.FEATURE_NAME == "Features"
        result = engine.evaluate(0.5)
        assert result.feature_name == "Features"

    def test_enrichment_suite_returns_all_engines(self):
        suite = VerifiablezkclinicalaudittrailEnrichmentSuite()
        results = suite.execute_all(primary_val=0.5, secondary_val=0.2)
        assert len(results) == 8
        for key, value in results.items():
            assert value.status == "OPTIMAL"

    def test_enrichment_suite_critical_escalation(self):
        suite = VerifiablezkclinicalaudittrailEnrichmentSuite()
        results = suite.execute_all(primary_val=10.0, secondary_val=5.0)
        for key, value in results.items():
            assert value.status in ("WARNING", "CRITICAL_ALERT")


class TestInputValidation:
    """Tests for input validation and bounds checking."""

    def test_system_task_payload_creation(self):
        payload = SystemTaskPayload(
            task_id="TEST-001",
            target_identifier="KEY-001",
            primary_metric=25.0,
            secondary_metric=10.0,
        )
        assert payload.task_id == "TEST-001"
        assert payload.is_critical_flag is False

    def test_system_task_payload_with_defaults(self):
        payload = SystemTaskPayload(
            task_id="TEST-002",
            target_identifier="KEY-002",
            primary_metric=15.0,
        )
        assert payload.secondary_metric == 0.0
        assert payload.status_descriptor == "NOMINAL"
