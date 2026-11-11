"""P0/SEC-01 regression tests: JWT secret fail-fast behavior."""
import pytest

from app.core.config import Settings, validate_security_settings


def test_production_without_jwt_secret_fails_fast():
    """ENV != 'dev' + missing JWT_SECRET must abort startup instead of
    silently using an insecure default (P0/SEC-01, DEP-01, DOC-04)."""
    s = Settings(ENV="production", JWT_SECRET="")
    with pytest.raises(RuntimeError) as exc:
        validate_security_settings(s)
    assert "JWT_SECRET" in str(exc.value)


def test_production_rejects_published_example_secret():
    """A secret copied verbatim from .env.example is publicly known and must
    be rejected in non-dev environments (P0/SEC-01 hardening)."""
    s = Settings(ENV="production", JWT_SECRET="ganti-ini-dengan-secret-acak-panjang")
    with pytest.raises(RuntimeError) as exc:
        validate_security_settings(s)
    assert "example value" in str(exc.value)


def test_production_with_jwt_secret_passes():
    s = Settings(ENV="production", JWT_SECRET="a" * 64)
    validate_security_settings(s)
    assert s.JWT_SECRET == "a" * 64


def test_dev_without_jwt_secret_gets_ephemeral_random_secret():
    """In dev, a missing secret is replaced with a random per-process value —
    never the old publicly-known default string."""
    s = Settings(ENV="dev", JWT_SECRET="")
    validate_security_settings(s)
    assert s.JWT_SECRET
    assert len(s.JWT_SECRET) >= 32
    assert s.JWT_SECRET != "super-secret-key-change-in-production-reqlint-hs256"


def test_dev_two_processes_get_different_ephemeral_secrets():
    s1 = Settings(ENV="dev", JWT_SECRET="")
    validate_security_settings(s1)
    s2 = Settings(ENV="dev", JWT_SECRET="")
    validate_security_settings(s2)
    assert s1.JWT_SECRET != s2.JWT_SECRET
