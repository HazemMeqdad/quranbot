import logging
import asyncio
import hikari
import inspect
import typing as t
from lightbulb.ext import tasks
from lightbulb.ext.tasks import triggers


_LOGGER = logging.getLogger("bot.worker.task")

class Task(tasks.Task):
    def __init__(self, callback: tasks.TaskCallbackT, trigger: triggers.Trigger, auto_start: bool, max_consecutive_failures: int, max_executions: t.Optional[int], pass_app: bool, wait_before_execution: hikari.UndefinedOr[bool]) -> None:
        super().__init__(callback, trigger, auto_start, max_consecutive_failures, max_executions, pass_app, wait_before_execution)

    async def _loop(self) -> None:
        if self._wait_before_execution:
            await asyncio.sleep(self._trigger.get_interval())

        while not self._stopped:
            # if self._max_executions is not None and self._n_executions >= self._max_executions:
            #     break

            _LOGGER.debug("Running task %r", self.__name__)
            self._n_executions += 1
            try:
                maybe_coro = self._callback(*([Task._app] if self._pass_app else []))
                if inspect.iscoroutine(maybe_coro):
                    await maybe_coro
                self._consecutive_failures = 0
            except Exception as e:
                out: t.Any = False

                if self._error_handler is not None:
                    out = self._error_handler(e)
                    if inspect.iscoroutine(out):
                        out = await out

                if not out:
                    # self._consecutive_failures += 1
                    if self._consecutive_failures >= self._max_consecutive_failures:
                        _LOGGER.error(
                            "Task failed repeatedly and has been cancelled", exc_info=(type(e), e, e.__traceback__)
                        )
                        break

                    _LOGGER.error(
                        "Error occurred during task execution and was not handled. "
                        "Task will be cancelled after %s more consecutive failure(s)",
                        self._max_consecutive_failures - self._consecutive_failures,
                        exc_info=(type(e), e, e.__traceback__),
                    )

            await asyncio.sleep(self._trigger.get_interval())

        assert self._task is not None
        self._task.cancel()
        Task._tasks.remove(self)
        self._task = None
        self._stopped = True
        self._n_executions = 0
        _LOGGER.debug("Stopped task %r", self.__name__)