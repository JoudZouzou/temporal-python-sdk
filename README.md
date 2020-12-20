# Unofficial Python SDK for the Temporal Workflow Engine

## Status

This should be considered EXPERIMENTAL at the moment. At the moment, all I can say is that the [test cases](https://gist.github.com/firdaus/4ec442f2c626122ad0c8d379a7ffd8bc) currently pass. I have not tested this for any real world use cases yet. 

## Roadmap 

1.0
- [x]  Workflow argument passing and return values
- [x]  Activity invocation
- [x]  Activity heartbeat and Activity.getHeartbeatDetails()
- [x]  doNotCompleteOnReturn
- [x]  ActivityCompletionClient
    - [x]  complete
    - [x]  complete_exceptionally
- [x]  Activity get_namespace(), get_task_token() get_workflow_execution()
- [x]  Activity Retry
- [x]  Activity Failure Exceptions
- [x] workflow_execution_timeout / workflow_run_timeout / workflow_task_timeout
- [x] Workflow exceptions
- [x]  Cron workflows
- [x]  Workflow static methods:
    - [x]  await_till()
    - [x]  sleep()
    - [x]  current_time_millis()
    - [x]  now()
    - [x]  random_uuid()
    - [x]  new_random()
    - [x]  get_workflow_id()
    - [x]  get_run_id()
    - [x]  get_version()
    - [x]  get_logger()
- [x]  Activity invocation parameters
- [x]  Query method
- [x]  Signal methods
- [x]  Workflow start parameters - workflow_id etc...
- [x]  Workflow client - starting workflows synchronously
- [x]  Workflow client - starting workflows asynchronously (WorkflowClient.start)
- [x]  Get workflow result after async execution (client.wait_for_close)
- [x]  Workflow client - invoking signals
- [x]  Workflow client - invoking queries

1.1
- [x] ActivityStub and Workflow.newUntypedActivityStub
- [ ] Classes as arguments and return values to/from activity and workflow methods (DataConverter)
- [ ] WorkflowStub and WorkflowClient.newUntypedWorkflowStub
- [ ] Custom workflow ids through start() and new_workflow_stub()
- [ ] ContinueAsNew
- [ ] Parallel activity execution (STATUS: there's a working but not finalized API).
- [ ] Compatibility with Java client
- [ ] Compatibility with Golang client
- [ ] Remove threading, use coroutines for everything all concurrency 

2.0
- [ ] Sticky workflows

Post 2.0:
- [ ] sideEffect/mutableSideEffect
- [ ] Local activity
- [ ] Timers
- [ ] Cancellation Scopes
- [ ] Child Workflows
- [ ] Explicit activity ids for activity invocations
