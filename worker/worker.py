import queue
import gevent
import asyncio
import time
import scripts.queue_utils as utils
from scripts.queue_utils import CONFIG


class Worker(object):
    def __init__(self):
        self._waiting_time = 0
        self._customers_served = 0
        self._total_execution_time = 0
        self._poll_queue_interval = CONFIG["poll_queue_interval"]
        self._execution_time = utils.get_execution_time()

    def execute_job(self, customers_queue, done, queue_stats):
        while not done.is_set() or not customers_queue.empty():
            queue_stats.set_max_queue_size(customers_queue)
            try:
                customer = customers_queue.get_nowait()
                customer.set_time_in_queue(time.time())
            except queue.Empty:
                gevent.sleep(self._poll_queue_interval)
                self._waiting_time += self._poll_queue_interval
                continue
            self._customers_served += 1
            gevent.sleep(self._execution_time)
            customer.set_time_waited(time.time())
            self._total_execution_time += self._execution_time

    def get_total_waiting_time(self):
        return self._waiting_time

    def get_total_working_time(self):
        return self._total_execution_time

    def get_total_customers_served(self):
        return self._customers_served


class AsyncWorker(Worker):
    def __init__(self):
        super().__init__()

    async def execute_job(self, customers_queue, done, queue_stats):
        while not done.is_set() or not customers_queue.empty():
            queue_stats.set_max_queue_size(customers_queue)
            try:
                customer = customers_queue.get_nowait()
                customer.set_time_in_queue(time.time())
            except asyncio.queues.QueueEmpty:
                await asyncio.sleep(self._poll_queue_interval)
                self._waiting_time += self._poll_queue_interval
                continue
            self._customers_served += 1
            customer.set_time_waited(time.time())
            await asyncio.sleep(self._execution_time)
            self._total_execution_time += self._execution_time
        customers_queue.task_done()
