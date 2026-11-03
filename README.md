# distributed-task-executor

A project to showcase a distributed task executor.

### Components
Task Queue
State Store
Heartbeat & Membership
Dead Letter handling
Scheduler / Clock trigger 

### Operationals
Failure Recovery / Retry system
Concurrency & Rate limiting
Observability / Health checks

#state management #ode dynamics #communication, and #system failures

### Objects / Participants
- API Listener
- State Store
- Task Queue
- Orchestrator Watchdog
- Worker

The State Store and Task Queue are designed as ports, so their implementations can be replaced (in progress, see #10). See `GLOSSARY.md` for the meaning of these terms.

### Task Sequence
```Mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Listener as API Listener
    participant DB as State Store
    participant Queue as Task Queue
    participant Orch as Orchestrator Watchdog
    participant Worker

    %% Task Submission Phase
    rect rgb(240, 244, 248)
    note over Client, Queue: 1. Submission & Ingestion Phase
    Client->>Listener: POST /tasks (Task Payload)
    activate Listener
    Listener->>DB: Write Task (status = "Pending")
    Listener->>Queue: Push Task ID
    Listener-->>Client: 202 Accepted (returns task_id)
    deactivate Listener
    end

    %% Dispatch & Execution Phase
    rect rgb(245, 248, 240)
    note over Queue, Worker: 2. Claim & Execution Phase
    Worker->>Queue: Pop Next Task ID
    activate Worker
    Queue-->>Worker: Return Task ID
    Worker->>DB: Acquire Lease (status = "Running", assigned_worker = worker_id, lease_ttl)
    
    loop Heartbeat Loop (Every N seconds)
        Worker->>DB: Send Heartbeat (extend lease_ttl)
    end

    Worker->>Worker: Execute Task Logic
    
    alt Worker still holds the Lease
        alt Successful Completion
            Worker->>DB: Update Task (status = "Succeeded", result_data) and release Lease
        else Task Runtime Error
            Worker->>DB: Update Task (status = "Failed", error_details) and release Lease
        end
    else Lease was lost
        Worker->>DB: Report rejected, Task unchanged, late report kept in Crash Report
    end
    deactivate Worker
    end

    %% Fault Recovery / Timeout Sweep
    rect rgb(253, 242, 242)
    note over Orch, DB: 3. Resilience & Sweep Phase (Watchdog Loop)
    loop Periodic Health Sweep (e.g., every 10s)
        Orch->>DB: Query Tasks where status = "Running" AND lease_ttl expired
        Orch->>DB: Mark each expired Task (status = "Failed") and save a Crash Report

        Orch->>DB: Query Tasks where status = "Failed"
        Orch->>DB: Check retry_count < retry_limit
        alt Retries Available
            Orch->>DB: Retry Task (status = "Pending", retry_count + 1)
            Orch->>Queue: Re-queue Task ID
        else Retry Limit Reached
            Orch->>DB: Mark Task (status = "Dead Letter")
        end

        Orch->>DB: Query Tasks stuck in status = "Pending" past the time limit
        Orch->>Queue: Re-queue Task ID
    end
    end
```

### Acknowledgements
Thank you to [Matt Pocock](https://www.aihero.dev) for the [engineering skills for coding agents](https://github.com/mattpocock/skills). The glossary, the build plan and the workflow in `CLAUDE.md` all came out of working with them, and they made this project better.