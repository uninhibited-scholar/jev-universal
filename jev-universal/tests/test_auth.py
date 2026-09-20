import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jev_universal.auth import JWTVerifier
from jev_universal.server import create_server
from starlette.testclient import TestClient

ISSUER = "https://issuer.example.com/"
RESOURCE = "https://jev.example.com/mcp"


@pytest.fixture
def signing():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def token(key, **changes):
    claims = {
        "iss": ISSUER,
        "aud": RESOURCE,
        "exp": int(time.time()) + 600,
        "sub": "test-user",
        "scope": "jev:use",
    }
    claims.update(changes)
    return jwt.encode(claims, key, algorithm="RS256")


def verifier(monkeypatch, key):
    v = JWTVerifier(ISSUER, "https://issuer.example.com/jwks", RESOURCE)
    monkeypatch.setattr(
        v.jwks, "get_signing_key_from_jwt", lambda t: SimpleNamespace(key=key.public_key())
    )
    return v


async def test_valid_token(monkeypatch, signing):
    access = await verifier(monkeypatch, signing).verify_token(token(signing))
    assert access.resource == RESOURCE
    assert access.scopes == ["jev:use"]


@pytest.mark.parametrize(
    "changes",
    [{"aud": "another-app"}, {"iss": "https://evil.example/"}, {"exp": 1}, {"scope": ["jev:use"]}],
)
async def test_invalid_token(monkeypatch, signing, changes):
    assert await verifier(monkeypatch, signing).verify_token(token(signing, **changes)) is None


async def test_bad_signature(monkeypatch, signing):
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    assert await verifier(monkeypatch, signing).verify_token(token(other)) is None


def test_public_binding_requires_auth(monkeypatch):
    monkeypatch.setenv("JEV_HOST", "0.0.0.0")
    for name in ["JEV_PUBLIC_URL", "JEV_OAUTH_ISSUER", "JEV_OAUTH_JWKS_URL"]:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match="requires OAuth"):
        create_server()


def test_http_auth_and_discovery(monkeypatch, signing):
    monkeypatch.setenv("JEV_PUBLIC_URL", RESOURCE)
    monkeypatch.setenv("JEV_OAUTH_ISSUER", ISSUER)
    monkeypatch.setenv("JEV_OAUTH_JWKS_URL", "https://issuer.example.com/jwks")
    monkeypatch.setattr(
        jwt.PyJWKClient,
        "get_signing_key_from_jwt",
        lambda self, t: SimpleNamespace(key=signing.public_key()),
    )
    server = create_server()
    app = server.streamable_http_app()
    headers = {"Accept": "application/json, text/event-stream"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    }
    with TestClient(app, base_url="https://jev.example.com") as client:
        assert client.post("/mcp", json=payload, headers=headers).status_code == 401
        assert (
            client.post(
                "/mcp", json=payload, headers={**headers, "Authorization": "Bearer invalid"}
            ).status_code
            == 401
        )
        assert (
            client.post(
                "/mcp",
                json=payload,
                headers={**headers, "Authorization": "Bearer " + token(signing, scope="other")},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/mcp",
                json=payload,
                headers={**headers, "Authorization": "Bearer " + token(signing)},
            ).status_code
            == 200
        )
        metadata = client.get("/.well-known/oauth-protected-resource/mcp")
        assert metadata.status_code == 200
        assert metadata.json()["resource"] == RESOURCE
        assert metadata.json()["authorization_servers"] == [ISSUER]
