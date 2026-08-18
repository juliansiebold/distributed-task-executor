# distributed-task-executor

### Components
Queue (Dispatcher)
State Store
Heartbeat & Membership
Dead Letter Queue
Scheduler / Clock trigger 

### Operationals
Failure Recovery / Retry system
Concurrency & Rate limiting
Observability / Health checks

#state management #ode dynamics #communication, and #system failures

### Flow Diagram
```Mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Listener as API Listener
    participant DB as State Store (Postgres)
    participant Queue as Task Queue (Redis/MQ)
    participant Orch as Orchestrator Watchdog
    participant Worker

    %% Task Submission Phase
    rect rgb(240, 244, 248)
    note over Client, Queue: 1. Submission & Ingestion Phase
    Client->>Listener: POST /tasks (payload, parameters)
    activate Listener
    Listener->>DB: Write task record (status = "PENDING")
    Listener->>Queue: Push Task ID to Queue
    Listener-->>Client: 202 Accepted (returns task_id)
    deactivate Listener
    end

    %% Dispatch & Execution Phase
    rect rgb(245, 248, 240)
    note over Queue, Worker: 2. Claim & Execution Phase
    Worker->>Queue: Pop / Lease Next Task ID
    activate Worker
    Queue-->>Worker: Return Task ID
    Worker->>DB: Acquire Lease Lock (status = "RUNNING", assigned_worker = worker_id, lease_ttl)
    
    loop Heartbeat Loop (Every N seconds)
        Worker->>DB: Send Heartbeat (extend lease_ttl)
    end

    Worker->>Worker: Execute Task Logic
    
    alt Successful Completion
        Worker->>DB: Update Record (status = "SUCCESS", result_data)
    else Task Runtime Error
        Worker->>DB: Update Record (status = "FAILED", error_details)
    end
    deactivate Worker
    end

    %% Fault Recovery / Timeout Sweep
    rect rgb(253, 242, 242)
    note over Orch, DB: 3. Resilience & Sweep Phase (Orchestrator Loop)
    loop Periodic Health Sweep (e.g., every 10s)
        Orch->>DB: Query tasks where status = "RUNNING" AND lease_ttl expired
        
        alt Worker Crashed / Unresponsive
            Orch->>DB: Check retry_count < max_retries
            alt Retries Available
                Orch->>DB: Reset Task (status = "PENDING", retry_count + 1)
                Orch->>Queue: Re-queue Task ID
            else Max Retries Exceeded
                Orch->>DB: Mark Task (status = "DEAD_LETTER")
            end
        end
    end
    end
```