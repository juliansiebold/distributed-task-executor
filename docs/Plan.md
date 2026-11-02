# Build Plan

## Next step

- **Issue:** [#16](https://github.com/juliansiebold/distributed-task-executor/issues/16) Restructure into one package with a working entry point
- **Handoff:** [comment on #16](https://github.com/juliansiebold/distributed-task-executor/issues/16#issuecomment-6589290171)

## About this plan

This is a showcase codebase: built to production standards and deliberately overkill, but run locally. Running it on production infrastructure is out of scope, and the design leaves that open for later.

**The goal:** a reviewer starts the system with one command, kills a Worker in the middle of a Task, and watches the Task recover with nothing lost. The code should hold up when they read it afterwards.

Every feature is judged by whether it strengthens that moment or that code.

This file holds the order and the reasoning. [Issues](https://github.com/juliansiebold/distributed-task-executor/issues) hold what to build and when each is done, and the [project board](https://github.com/users/juliansiebold/projects/1) holds status. `GLOSSARY.md` defines the terms used here.

## Target layout

```
src/distributed_task_executor/
├── cli.py          # entry point: demo, api, worker, watchdog
├── core/           # Task and its lifecycle
├── application/    # use cases, ports, Lease
├── adapters/       # fakeredis, SQLite, timer, clock
└── services/       # api, worker, watchdog, dashboard
tests/              # lifecycle, contract, chaos
```

**Dependency rule**, enforced by `import-linter`:

```
cli
 ├── services   (driving adapters)
 └── adapters   (driven adapters)
      application
           core
```

Each layer may import only the layers below it. `services` and `adapters` may not import each other, and `cli` is the only place that connects them. See [ADR 003](adr/003-full-hexagon-for-a-showcase.md) and [ADR 004](adr/004-async-throughout.md).

## Milestones

The build starts with one thin end-to-end slice and then adds failure paths, so the system can be demonstrated early and mistakes in the ports appear before much depends on them. Issues are listed in build order.

### 1. Hexagon and first Task end to end

One Task goes from `POST /tasks` to Succeeded across separate processes.

- [#16](https://github.com/juliansiebold/distributed-task-executor/issues/16) Restructure into one package with a working entry point
- [#7](https://github.com/juliansiebold/distributed-task-executor/issues/7) Complete the Task lifecycle
- [#8](https://github.com/juliansiebold/distributed-task-executor/issues/8) New Tasks always start Pending
- [#11](https://github.com/juliansiebold/distributed-task-executor/issues/11) Task state transition test suite
- [#10](https://github.com/juliansiebold/distributed-task-executor/issues/10) Define State Store and Task Queue ports
- [#9](https://github.com/juliansiebold/distributed-task-executor/issues/9) Create app config
- [#3](https://github.com/juliansiebold/distributed-task-executor/issues/3) fakeredis adapter
- [#6](https://github.com/juliansiebold/distributed-task-executor/issues/6) Map Tasks to and from storage
- [#5](https://github.com/juliansiebold/distributed-task-executor/issues/5) Wire adapters at startup
- [#12](https://github.com/juliansiebold/distributed-task-executor/issues/12) API Listener
- [#13](https://github.com/juliansiebold/distributed-task-executor/issues/13) Worker

### 2. Recovery

A Task survives a crashed Worker, and a Task that keeps failing ends in Dead Letter.

- [#18](https://github.com/juliansiebold/distributed-task-executor/issues/18) Crash Reports
- [#14](https://github.com/juliansiebold/distributed-task-executor/issues/14) Orchestrator Watchdog
- [#17](https://github.com/juliansiebold/distributed-task-executor/issues/17) Worker handles a lost Lease
- [#19](https://github.com/juliansiebold/distributed-task-executor/issues/19) Retry backoff

### 3. Demo and chaos tests

The headline moment, and the proof behind it.

- [#20](https://github.com/juliansiebold/distributed-task-executor/issues/20) demo command and dashboard
- [#21](https://github.com/juliansiebold/distributed-task-executor/issues/21) Chaos tests

**The project is presentable at the end of this milestone.**

### 4. Observability and Worker shutdown

- [#22](https://github.com/juliansiebold/distributed-task-executor/issues/22) Logs, metrics and health endpoints
- [#23](https://github.com/juliansiebold/distributed-task-executor/issues/23) Graceful Worker shutdown

### 5. Second wave

A bonus, led by the SQLite adapter because a hexagon with one adapter proves nothing.

- [#24](https://github.com/juliansiebold/distributed-task-executor/issues/24) SQLite State Store adapter
- [#25](https://github.com/juliansiebold/distributed-task-executor/issues/25) Worker membership
- [#26](https://github.com/juliansiebold/distributed-task-executor/issues/26) Worker concurrency limits

## Time budget

An estimate, not a commitment: 4 to 6 weeks of evenings and weekends through milestone 4, plus about 2 more for the second wave.

## Parked

These are out of scope for now and have no issues, because they don't strengthen the recovery story:

- Scheduler / clock trigger
- Rate limiting

Also left out on purpose:

- **A code-running Task Runner:** the timer is the only adapter for now, and the port leaves room for a real one.
- **Grafana and distributed tracing:** both would need more infrastructure.
- **Docker and real Redis:** the demo runs with `uv run` on fakeredis in server mode. A real Redis later is a connection change.
