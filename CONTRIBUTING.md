# Contributing

Agent Watchtower is an alpha project. Small, concrete feedback is more useful than broad platform ideas right now.

Good contributions:

- install or quick-start failures
- clearer README wording
- real interrupted-agent examples
- small CLI bug fixes
- tests for resume, status, or artifact behavior

Please keep v0 narrow:

- no background daemon
- no messaging platform
- no plugin system
- no account, cloud, or payment automation

Before sending a pull request, run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -q
./scripts/release_preflight.sh
```

If you are not sure whether an idea fits v0, open an issue first.
