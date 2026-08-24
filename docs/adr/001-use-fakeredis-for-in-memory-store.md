### ADR 001: Selection of `fakeredis` for In-Memory Queue & State Emulation

* **Status:** Accepted
* **Date:** August 24, 2026
* **Deciders:** Julian (Software Architect / Lead)

---

#### Context & Problem Statement

To prove the core architectural concepts of a distributed task executor—including task dispatch, worker lease locking, heartbeat tracking, and failure recovery—the system requires a message queue and a shared key-value store.

The primary goal of this project is portfolio demonstration and architectural proof-of-concept (PoC). Traditional external infrastructure (such as running Docker containers with standalone Redis or MySQL instances) adds operational setup friction and distracts from core application logic, concurrency handling, and state-machine correctness.

We need a lightweight, zero-dependency storage layer that provides realistic Redis semantics without requiring external system services or Docker orchestration.

---

#### Decision Drivers

* **Zero Infrastructure Friction:** Developers and reviewers must be able to clone and run the repository immediately using standard Python toolchains (`uv`).
* **Realistic API Semantics:** Must support standard Redis primitives (`BRPOP`, `SET` with `NX`/`PX` for distributed leases, pub/sub, key expiry) to ensure code structures closely mirror real-world production implementations.
* **Process Isolation & Testability:** Must support both shared process memory and easy mocking for fast automated testing and multi-process local runs.

---

#### Considered Options

1. **Native Local Redis Server (`redis-server`)**
2. **SQLite Database (`tasks.db`)**
3. **`fakeredis` In-Memory Redis Emulator**

---

#### Decision Outcome

**Chosen Option:** **`fakeredis`**

We will use `fakeredis` to back both the Task Queue and the State Store during the proof-of-concept phase. Services will interact with standard `redis-py` client interfaces, backed in-memory by `fakeredis`.

---

#### Positive Consequences

* **Immediate Setup:** Zero external software dependencies or background daemons required. Running `uv sync` installs all required packages.
* **Production-Identical Code:** Services interact with `redis-py` standard methods. If the project is ever migrated to a standalone Redis cluster, no application code needs rewriting—only the client connection string changes.
* **Deterministic Testing:** Tests run in isolation with instant setup/teardown times, bypassing network I/O overhead.

#### Negative Consequences & Mitigations

* **In-Memory Volatility:** Data does not persist across application restarts.
* *Mitigation:* Acceptable for a PoC. Test scripts can seed initial state as needed.


* **Cross-Process Memory Boundaries:** By default, standard `fakeredis` instances exist within a single Python process memory space.
* *Mitigation:* For multi-process terminal demonstrations (e.g., separate worker processes), `fakeredis` can be run in a lightweight server mode or backed by a shared local server script when testing cross-process concurrency.



---