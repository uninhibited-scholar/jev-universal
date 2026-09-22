"""OAuth resource server for self-hosted deployments with an external issuer."""

import asyncio
from urllib.parse import urlsplit

import jwt
from mcp.server.auth.provider import AccessToken


def https_url(value: str, label: str) -> str:
    parts = urlsplit(value)
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{label} must include a valid port in 1-65535 when specified") from exc
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.fragment
        or parts.query
    ):
        raise ValueError(
            f"{label} must be an absolute HTTPS URL without credentials/query/fragment"
        )
    if port is not None and not 1 <= port <= 65535:
        raise ValueError(f"{label} must include a valid port in 1-65535 when specified")
    return value


class JWTVerifier:
    def __init__(self, issuer: str, jwks_url: str, resource: str):
        self.issuer = https_url(issuer, "JEV_OAUTH_ISSUER")
        self.resource = https_url(resource, "JEV_PUBLIC_URL")
        self.jwks = jwt.PyJWKClient(https_url(jwks_url, "JEV_OAUTH_JWKS_URL"), timeout=5)

    async def verify_token(self, token: str) -> AccessToken | None:
        if len(token) > 16384:
            return None
        try:
            key = await asyncio.to_thread(self.jwks.get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=["RS256", "ES256"],
                audience=self.resource,
                issuer=self.issuer,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
            scope = claims.get("scope", "")
            subject = claims["sub"]
            if not isinstance(scope, str) or not isinstance(subject, str) or not subject:
                return None
            return AccessToken(
                token=token,
                client_id=str(claims.get("client_id", claims.get("azp", subject))),
                subject=subject,
                scopes=scope.split(),
                expires_at=int(claims["exp"]),
                resource=self.resource,
            )
        except (jwt.PyJWTError, ValueError, TypeError, OSError):
            return None
