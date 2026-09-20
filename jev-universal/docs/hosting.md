# ChatGPT and remote hosting

Two supported integration designs: private Secure MCP Tunnel, or a self-hosted
OAuth resource server. Neither creates a shared hosted service on your behalf.
Local HTTP transport and OAuth validation are tested; an actual ChatGPT account
connection still requires that account's access and credentials.

## Option 1 — private Secure MCP Tunnel

1. Run `jev-universal --env-file /absolute/path/private.env --transport streamable-http`.
2. Obtain a tunnel and runtime credential from OpenAI Platform tunnel settings.
3. Follow the official `tunnel-client` quickstart, setting its private MCP URL to
   `http://127.0.0.1:8765/mcp`. Keep the tunnel process running. Associate the tunnel
   with the intended ChatGPT workspace as well as the Platform organization.
4. In ChatGPT developer mode, add the connection with **Tunnel**, select your
   tunnel, discover the four tools and try a pinned-content request first.
5. Then try a real classification. It consumes your TypeSafe quota.

Use the current commands from [OpenAI's tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
Tunnel permissions and ChatGPT developer-mode permissions are separate. This path
keeps the server bound to loopback and relies on the tunnel's access controls.

## Option 2 — HTTPS with an external OAuth issuer

This server implements the **resource-server side** of OAuth. Bring an authorization
server with OAuth metadata, authorization-code/PKCE support and JWT access tokens.
Configure client registration there (pre-registered clients or a supported registration
method), including the exact redirect URI supplied by ChatGPT. Grant only intended
users access to the `jev:use` scope.

Set these variables in your server's private environment:

```dotenv
TYPESAFE_API_KEY_FILE=/run/secrets/typesafe_key
JEV_HOST=0.0.0.0
JEV_PORT=8765
JEV_PUBLIC_URL=https://jev.example.com/mcp
JEV_OAUTH_ISSUER=https://issuer.example.com/
JEV_OAUTH_JWKS_URL=https://issuer.example.com/.well-known/jwks.json
```

Configure the issuer to issue **RS256 or ES256 access tokens** with:

- `iss` exactly equal to `JEV_OAUTH_ISSUER`;
- `aud` equal to `JEV_PUBLIC_URL`;
- valid `exp`, nonempty `sub`, and space-delimited `scope` containing `jev:use`.

The server checks signature, issuer, expiry and audience and enforces scope through
the MCP SDK. It publishes OAuth Protected Resource Metadata at
`/.well-known/oauth-protected-resource/mcp`. It does not issue tokens or implement
an authorization/login UI. That is your external issuer's responsibility.

Terminate HTTPS at your reverse proxy. Preserve Host and forward `/mcp` and the
well-known metadata path to the service. Do not disable DNS rebinding protection.
Add proxy rate limits and restrict issuer access: all authorized users of one
instance share that instance's TypeSafe billing credentials.

Container build (from the repository root):

```sh
docker build -f jev-universal/deploy/Dockerfile -t jev-universal:0.2.0 jev-universal
```

Run with the private environment file and read-only secret mount, publishing only
to a local reverse proxy:

```sh
docker run --rm --env-file /absolute/path/server.env \
  --mount type=bind,src=/absolute/path/typesafe-key,dst=/run/secrets/typesafe_key,readonly \
  -p 127.0.0.1:8765:8765 jev-universal:0.2.0
```

The secret must be readable by container UID 10001. In ChatGPT, add your HTTPS
`/mcp` URL and complete OAuth using your issuer's configuration. Verify discovery,
pinned-content roundtrip, an authorized paid call, and access denial after revocation.
JWTs are checked until expiry; use short token lifetimes when immediate revocation
is required. This adapter does not query an introspection/revocation endpoint.

[Official ChatGPT connection steps](https://developers.openai.com/plugins/deploy/connect-chatgpt).
