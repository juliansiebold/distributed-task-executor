# ADR 002: Implementation of Polymorphic State Pattern for Task Transitions

**Status:** Accepted  
**Date:** September 13, 2026  
**Deciders:** Julian (Software Architect / Lead)

> **Amendment (November 2, 2026):** The State pattern stands, but three things have changed. The code is moving to the layout in [the build plan](../Plan.md), so the `src/packages` paths below are out of date. `Lease` and `WorkerId` stay out of core and live in `application/` beside the ports. Saves are conditional, checked against a Task version and the Lease token (see #10), and the lifecycle now includes Dead Letter (see `GLOSSARY.md`). This project is also now described as a showcase codebase rather than a proof-of-concept, and the wording below was updated to match.

> **Amendment (November 3, 2026):** `Task.transition_to`, `Task.increase_retry` and `Task.retry_count` are public on purpose. The State pattern accepts this collaboration between the Task and its states: the Task's actions delegate to the current state, and the state classes guard which transitions are allowed by raising `TaskException` for any move they don't permit. Hiding these members would protect against code calling them directly, which is not what this pattern is here to demonstrate.

---

## Context & Problem Statement

In a distributed task execution system, tasks transition through a defined lifecycle (`PENDING` $\rightarrow$ `RUNNING` $\rightarrow$ `SUCCEEDED` / `FAILED`). The domain layer must enforce valid state transition boundaries and encapsulate retry logic cleanly.

For production systems, domain state is frequently represented as a simple scalar string or enum, with lifecycle enforcement handled by an external workflow coordinator. However, as a **portfolio demonstration and showcase codebase**, this project aims to showcase object-oriented design (OOD) depth, explicit behavioral patterns, and strict domain encapsulation.

We needed to decide how to model task state lifecycle transitions while keeping domain entities strictly decoupled from runtime execution concerns (worker IDs, storage leases) and network serialization boundaries.

---

## Considered Options

1. **Option 1: Flat Enum with Service-Layer State Machine**
   * Tasks hold a scalar `status: TaskStatus` enum value.
   * Transition rules and validation live in an external application service via explicit transition matrices or conditional logic.
2. **Option 2: Polymorphic State Pattern with Storage Layer Mapping**
   * Tasks delegate transition lifecycle logic to polymorphic `AbstractTaskState` instances (`PendingState`, `RunningState`, etc.) in memory within the core domain boundary.
   * Translation into serializable payloads (JSON/DTOs) for persistence or transport is explicitly decoupled and owned by the service/storage layer.

---

## Decision Outcome

**Chosen Option:** **Option 2 (Polymorphic State Pattern with Storage Layer Mapping)**

We have implemented the behavioral **State Pattern** across `src/packages/core/models.py` and `task_state.py`, while establishing a strict mapping boundary in `src/packages/storage`.

### Architectural Boundary & Separation of Concerns

* **Core Domain Layer (`src/packages/core`):** Operates on rich, hydrated Python instances (`Task` and `AbstractTaskState`). State logic is polymorphic, self-contained, and completely ignorant of persistence mechanisms or network formats. Execution concerns like `WorkerId` and storage leases remain excluded from domain models.
* **Storage & Service Layer (`src/packages/storage`, `src/packages/services`):** Owns write-backs, upserts, and serialization. When state transitions complete, a mapper/serializer translates the domain entity—extracting `TaskStatus` string values—into JSON DTOs for Redis persistence. On read, the storage layer rehydrates scalar JSON state back into concrete `AbstractTaskState` instances.

---

## Strategic Justification & Trade-offs

### Portfolio & Architectural Objectives
* **Design Depth:** Demonstrates advanced OOD principles, open-closed principle (OCP), and polymorphic dispatches to engineering reviewers.
* **Domain Purity:** `models.py` remains 100% agnostic of database schemas, JSON specifications, or Redis formats.
* **Clean Layering:** Proves an understanding of Enterprise Integration Patterns by isolating state machine behavior inside the domain while delegating translation/persistence to mappers in `storage/`.
* **Explicit Exception Contracts:** Disallowed transitions automatically raise targeted domain exceptions (`StartTaskException`, `TaskException`) without cluttering service logic with `if/else` checks.

### Production Realities & Technical Debt Acknowledgement
While Option 2 fulfills our showcase goals, we explicitly acknowledge its trade-offs compared to Option 1:

* **Hydration Overhead:** Every storage read operation requires a factory/mapper step to instantiate concrete state classes (`PendingState()`, `RunningState()`) rather than simply assigning an enum value.
* **Process Coupling:** Transmitting raw serialized DTOs across network boundaries is mandatory; attempting to directly pass hydrated polymorphic state objects across process boundaries would introduce severe code coupling.
