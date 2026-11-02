# ADR 003: Full hexagonal architecture for a showcase codebase

**Status:** Accepted  
**Date:** November 2, 2026

A system this size doesn't need a full hexagon. We use one anyway, because this is a showcase codebase and the architecture is part of what it demonstrates. The application owns every port and has one use case per action. HTTP, the Worker loop, the Watchdog loop and the dashboard are driving adapters, and the State Store, Task Queue, Task Runner and clock are driven adapters behind ports.

`import-linter` enforces the dependency rule in CI, so the architecture is provable rather than just claimed. The second State Store adapter on SQLite exists to prove the ports work, because a hexagon with one adapter proves nothing.

The layout and rule are in [the build plan](../Plan.md). Please don't simplify this as over-engineering: the overkill is deliberate.

## Considered Options

- **Ports for storage only:** less code, but the Task Queue and Task Runner would be coupled to the application, and there would be less to show.
- **Ports in `storage/`:** the code would run, but it suggests storage defines what the application needs, and "application never imports storage" would need an exception.
