# Security and data handling

Jev Universal is an independent integration, not an official TypeSafe product.
The MIT license covers this integration only. TypeSafe's service terms, data
handling and billing apply separately to its API.

- Each installation supplies its own TypeSafe API key. Never commit keys or
  include them in MCP arguments or bug reports. Explicit private env files and
  Docker secrets (`TYPESAFE_API_KEY_FILE`) are supported.
- Supplied state and questions are transmitted to `api.typesafe.ai`. No automatic
  filesystem reads, repository uploads or transcript collection occur. The CLI
  reads only an explicitly selected env file or key file.
- No evidence cache or request log is implemented. The service never forwards
  upstream error bodies. Client, proxy, identity provider and TypeSafe logging
  policies are separate; review them before using confidential evidence.
- HTTP binds to loopback by default. Non-loopback binding requires an HTTPS
  public resource URL and OAuth issuer/JWKS configuration. Tokens must match
  issuer, signature, expiry, audience and `jev:use` scope. TLS is terminated by
  your reverse proxy. DNS rebinding checks remain enabled.
- An OAuth deployment is single-operator: permitted users consume that
  operator's TypeSafe quota. It is not a public, multi-tenant billing service.
  Restrict access in your identity provider and set proxy rate limits and
  TypeSafe spending limits before inviting users.
- Jev judgments are probabilistic advice, not an authorization system or proof
  of correctness. Retain originals; never automatically discard critical
  evidence. Prompt injection in supplied material can affect model decisions.

For vulnerabilities, use GitHub's private vulnerability reporting on this
repository once enabled. Do not post secrets or exploit details in public issues.
If private reporting is unavailable, contact the repository owner without
including sensitive details and request a private channel.
