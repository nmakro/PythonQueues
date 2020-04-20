import asyncio
import time
from random import gauss, randint
from queue_utils import QueueStats, CONFIG

customers_arrived = 0


class Worker(object):
    def __init__(self):
        self._waiting_time = 0
        self._customers_served = 0
        self._total_working_time = 0
        self._poll_queue_interval = 0.1
        self._execution_time = abs(gauss(CONFIG["execution_mean"], CONFIG["execution_deviation"]))

    async def execute_job(self, customers_queue, done, queue_stats):
        while not done.is_set() or not customers_queue.empty() > 0:
            queue_stats.set_max_queue_size(customers_queue)
            try:
                customer = customers_queue.get_nowait()
            except asyncio.queues.QueueEmpty:
                await asyncio.sleep(self._poll_queue_interval)
                self._waiting_time += self._poll_queue_interval
                continue
            self._customers_served += 1
            customer.set_waiting_time_in_worker(self._execution_time)
            customer.set_time_waited(time.time())
            await asyncio.sleep(self._execution_time)
            customer.total_waiting_time(self._execution_time)
            self._total_working_time += self._execution_time
        customers_queue.task_done()

    def get_total_waiting_time(self):
        return self._waiting_time

    def get_total_working_time(self):
        return self._total_working_time

    def get_total_customers_served(self):
        return self._customers_served


class Customer(object):
    def __init__(self):
        self.customer_id = 0
        self.waiting_time = 0.0
        self.time_started_waiting = 0.0

    def set_time_started_waiting(self, time_started):
        self.time_started_waiting = time_started

    def set_time_waited(self, current_time):
        self.waiting_time = current_time - self.time_started_waiting

    def get_waiting_time(self):
        return self.waiting_time

    def set_customer_id(self, customer_id):
        self.customer_id = customer_id


def create_new_customers():
    customers = randint(0, 2)
    return customers


async def insert_new_customer_to_queue(customers_queue, customers, store_closed):
    global customers_arrived
    counter = 1
    "Simulate customers entering the store for 6 hours"
    while counter <= 360:
        counter += 1
        "Every minute some random number of customers between 0 - 3 arrive arrive in the store"
        customers_to_add = create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            await customers_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        await asyncio.sleep(0.1)
    store_closed.set()
    customers_queue.task_done()


async def work():
    q = asyncio.Queue()
    done = asyncio.Event()
    customers = []
    workers = []
    jobs = []

    for i in range(CONFIG["workers"]):
        worker = Worker()
        workers.append(worker)

    q_stats = QueueStats(workers, customers)
    for w in workers:
        jobs.append(w.execute_job(q, done, q_stats))
    c = insert_new_customer_to_queue(q, customers, done)
    jobs.append(c)

    await asyncio.gather(*jobs)

    q_stats.report()


if __name__ == '__main__':
    asyncio.run(work())
