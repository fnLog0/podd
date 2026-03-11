# Podd CLI

This workspace package adds a small `incur`-based CLI for local development tasks.

## Commands

- `podd paths`
- `podd config-show`
- `podd server-start`
- `podd esp-build`
- `podd esp-build --sim`

## Run

From the repo root:

```bash
pnpm cli --help
pnpm cli paths
pnpm cli esp-build --sim
```

Or directly:

```bash
pnpm --filter podd-cli exec node cli.mjs --help
```
