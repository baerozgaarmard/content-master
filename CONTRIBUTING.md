# Contributing to Content Master

We welcome contributions, showcases, and improvements to the **Content Master** suite!

## How to Contribute

1. Fork the repository (`https://github.com/baerozgaarmard/content-master`).
2. Create a topic branch: `git checkout -b feature/my-new-feature`.
3. Verify tests and linting:
   ```bash
   npm test
   npm run check
   ```
4. Commit your changes with clear commit messages.
5. Push to your branch and open a Pull Request.

## Monorepo Layout

- `packages/flick`: AI Motion Director for Remotion-based scene animations.
- `packages/faceless`: Character dialogue reel generator with Fish Audio & Minecraft background templates.
- `packages/mcp`: Content Master MCP client & connection utility for Codex and Claude Code.
- `skills/`: Root-level agent skills for direct `npx skills` installation.

## Community & Attribution

Maintained by **Bearozgaarmard** ([@baerozgaarmard](https://github.com/baerozgaarmard)).
Licensed under the [MIT License](LICENSE).
