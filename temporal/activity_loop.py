import asyncio
import datetime
import logging
import json
import inspect
from typing import List

from temporal.activity import ActivityContext, ActivityTask, complete_exceptionally, complete
from temporal.api.taskqueue.v1 import TaskQueue, TaskQueueMetadata
from temporal.conversions import from_payloads
from temporal.service_helpers import create_workflow_service, get_identity
from temporal.worker import Worker, StopRequestedException
from temporal.api.workflowservice.v1 import WorkflowServiceStub as WorkflowService, PollActivityTaskQueueRequest, \
    PollActivityTaskQueueResponse

logger = logging.getLogger(__name__)


def activity_task_loop(worker: Worker):
    asyncio.run(activity_task_loop_func(worker))


async def activity_task_loop_func(worker: Worker):
    service: WorkflowService = create_workflow_service(worker.host, worker.port, timeout=worker.get_timeout())
    worker.manage_service(service)
    logger.info(f"Activity task worker started: {get_identity()}")
    try:
        while True:
            if worker.is_stop_requested():
                return
            try:
                polling_start = datetime.datetime.now()
                polling_request: PollActivityTaskQueueRequest = PollActivityTaskQueueRequest()
                polling_request.task_queue_metadata = TaskQueueMetadata()
                polling_request.task_queue_metadata.max_tasks_per_second = 200000
                polling_request.namespace = worker.namespace
                polling_request.identity = get_identity()
                polling_request.task_queue = TaskQueue()
                polling_request.task_queue.name = worker.task_queue
                task: PollActivityTaskQueueResponse
                task = await service.poll_activity_task_queue(request=polling_request)
                polling_end = datetime.datetime.now()
                logger.debug("PollActivityTaskQueue: %dms", (polling_end - polling_start).total_seconds() * 1000)
            except StopRequestedException:
                return
            except Exception as ex:
                logger.error("PollActivityTaskQueue error: %s", ex)
                raise
            # -----
            # if err:
            #     logger.error("PollActivityTaskQueue failed: %s", err)
            #     continue
            # -----
            task_token = task.task_token
            if not task_token:
                logger.debug("PollActivityTaskQueue has no task_token (expected): %s", task)
                continue

            args: List[object] = from_payloads(task.input)
            print(args)
            logger.info(f"Request for activity: {task.activity_type.name}")
            fn = worker.activities.get(task.activity_type.name)
            if not fn:
                logger.error("Activity type not found: " + task.activity_type.name)
                continue

            process_start = datetime.datetime.now()
            activity_context = ActivityContext()
            activity_context.service = service
            activity_context.activity_task = ActivityTask.from_poll_for_activity_task_response(task)
            activity_context.namespace = worker.namespace
            try:
                ActivityContext.set(activity_context)
                if inspect.iscoroutinefunction(fn):
                    return_value = await fn(*args)
                else:
                    return_value = fn(*args)
                if activity_context.do_not_complete:
                    logger.info(f"Not completing activity {task.activity_type.name}({str(args)[1:-1]})")
                    continue
                await complete(service, task_token, return_value)
                # -----
                # if error:
                #     logger.error("Error invoking RespondActivityTaskCompleted: %s", error)
                # -----
                logger.info(
                    f"Activity {task.activity_type.name}({str(args)[1:-1]}) returned {json.dumps(return_value)}")
            except Exception as ex:
                logger.error(f"Activity {task.activity_type.name} failed: {type(ex).__name__}({ex})", exc_info=True)
                await complete_exceptionally(service, task_token, ex)
                # -----
                # if error:
                #     logger.error("Error invoking RespondActivityTaskFailed: %s", error)
                # -----
            finally:
                ActivityContext.set(None)
                process_end = datetime.datetime.now()
                logger.info("Process ActivityTask: %dms", (process_end - process_start).total_seconds() * 1000)
    finally:
        # noinspection PyBroadException
        try:
            service.channel.close()
        except Exception:
            logger.warning("service.close() failed", exc_info=True)
        worker.notify_thread_stopped()
