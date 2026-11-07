# Distributed Task Executor

A system that accepts Tasks from Clients and executes them on a pool of Workers, recovering when Workers crash or become unresponsive.

## Language

### Participants

**Client**:
The person or thing that submits a Task and receives its Task ID.
_Avoid_: Caller, creator, user, submitter

**Client ID**:
The identifier of the Client that submitted a Task.

**API Listener**:
The entry point that accepts a submitted Task, records it and places it on the Task Queue.
_Avoid_: Server, gateway, ingestion service

**Worker**:
A process that claims Tasks from the Task Queue and executes them.
_Avoid_: Executor, node, consumer

**Orchestrator Watchdog**:
The periodic overseer that fails Tasks whose Lease has expired and decides whether each Failed Task is retried or sent to Dead Letter.
_Avoid_: Orchestrator (alone), monitor, supervisor

**Task Queue**:
The ordered line of Task IDs waiting to be claimed by a Worker. It holds references to Tasks, never their state.
_Avoid_: Queue (alone), dispatcher, broker

**State Store**:
The system of record for each Task's current state and Lease.
_Avoid_: Database, DB, repository

### Task

**Task**:
A single unit of work submitted for execution, tracked from submission to its final outcome.
_Avoid_: Job, record

**Task ID**:
The identifier that refers to one Task for its whole life, across every retry.

**Task Payload**:
The data a Task carries that describes the work to perform.
_Avoid_: Parameters, arguments

**Task Runner**:
The replaceable capability a Worker uses to perform a Task's work, which can be cancelled while in progress.
_Avoid_: Handler, executor

### Task lifecycle

**Attempt**:
One Worker's single try at a Task, numbered in the order the Task was claimed.
_Avoid_: Run, try, execution

**Pending**:
The state of a Task that is waiting for a Worker to claim it.
_Avoid_: Queued, init, initial

**Running**:
The state of a Task that a Worker is executing.
_Avoid_: Active, in progress

**Succeeded**:
The final state of a Task whose execution completed without error.
_Avoid_: Success, done, completed

**Failed**:
The state of a Task whose latest attempt ended in an error or an expired Lease, and whose next step has not yet been decided.
_Avoid_: Error, crashed

**Retry**:
The return of a Failed Task to Pending so that a Worker can claim it for another attempt.
_Avoid_: Restart, re-run

**Retry limit**:
The number of Retries a Task may use before a failure sends it to Dead Letter.
_Avoid_: Max retries, max attempts

**Dead Letter**:
The final state of a Failed Task that has no Retries left.
_Avoid_: Dead Letter Queue, DLQ, abandoned

### Ownership

**Lease**:
A Worker's exclusive, time-limited claim on one Task.
_Avoid_: Lock, lease lock, assignment

**Heartbeat**:
A Worker's periodic renewal of its Lease, signalling that it is still alive.
_Avoid_: Ping, keepalive

**Crash Report**:
The saved record of a Lease that expired, including the Worker's late report if one ever arrives.
_Avoid_: Rejected report, failure log
