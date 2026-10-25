# Content Master MCP

Connect Content Master to Claude Code or Codex through Content Master's hosted MCP server.

## Start here

- [MCP overview](docs/mcp.md)
- [Connect with Claude Code](docs/claude.md)
- [Connect with Codex](docs/codex.md)
- [Tool reference](docs/tools.md)

Give this repository to Claude Code or Codex:

```text
https://github.com/baerozgaarmard/content-master

Connect Content Master using the instructions for my client in this repository. Show me each command before running it, wait for my approval, preserve my other MCP connections, and verify the connection with a Content Master tool before claiming success.
```

The recommended path uses the official command provided by Claude Code or Codex. The agent can prepare the command, but you review and approve it. You personally complete Content Master sign-in and consent.

## Hosted MCP endpoint

```text
https://github.com/baerozgaarmard/content-master/api/mcp
```

No Content Master API key or `Authorization` header is required during setup. The client discovers Content Master's OAuth flow from the endpoint and stores its own authentication securely.

## Optional CLI fallback

The dependency-free CLI is available for diagnostics, removal, or environments where the direct setup instructions cannot be used.

Claude Code:

```powershell
npx --yes github:baerozgaarmard/content-master install --client claude
```

Codex:

```powershell
npx --yes github:baerozgaarmard/content-master install --client codex
```

The installer shows the exact configuration change and asks for confirmation. Add the installer's `--yes` option only when you deliberately want to skip that confirmation.

### CLI commands

```powershell
# Preview without changing configuration
npx --yes github:baerozgaarmard/content-master install --client claude --dry-run

# Check configuration and endpoint reachability
npx --yes github:baerozgaarmard/content-master status --client claude

# Remove only the Content Master entry
npx --yes github:baerozgaarmard/content-master remove --client claude
```

Replace `claude` with `codex` when using Codex.

## Safety

- The default MCP name is `content-master`.
- The CLI refuses to overwrite a different MCP entry with the same name.
- Production endpoints must use HTTPS.
- Do not give an agent your Content Master password, OAuth token, or browser session.

## Development

```powershell
git clone https://github.com/baerozgaarmard/content-master.git
cd content-master-mcp
npm test
npm run check
```

The CLI requires Node.js 18 or newer and has no runtime dependencies.

## License

MIT © 2026 Bearozgaarmard. See [LICENSE](LICENSE).
