# ADR 004: Async throughout

**Status:** Accepted  
**Date:** November 2, 2026

The application and all its ports are async. A Worker has to send Heartbeats while a Task runs and cancel that Task if a Heartbeat is refused, and `asyncio` makes both straightforward for the timer Task Runner. This is expensive to reverse, because async spreads into every port and adapter.

## Considered Options

- **Threads with synchronous ports:** simpler to read, but a running Task can't be cancelled cleanly.

## Consequences

A future code-running Task Runner can't run blocking work on the event loop, or Heartbeats would stop and the Lease would expire. It needs its own subprocess, which also gives it a clean way to be cancelled.
