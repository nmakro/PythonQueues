import asyncio
import time
from random import gauss, randint, choice
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
            customer.set_time_waited(time.time())
            await asyncio.sleep(self._execution_time)
            customer.total_waiting_time(self._execution_time)
            self._total_working_time += self._execution_time

    def get_total_waiting_time(self):
        return self._waiting_time

    def get_total_working_time(self):
        return self._total_working_time

    def get_total_customers_served(self):
        return self._customers_served


class Customer(object):
    def __init__(self):
        self.customer_id = 0
        self._waiting_time = 0.0
        self._time_started_waiting = 0.0

    def set_time_started_waiting(self, time_started):
        self._time_started_waiting = time_started

    def set_time_waited(self, current_time):
        self._waiting_time = current_time - self._time_started_waiting

    def get_waiting_time(self):
        return self._waiting_time

    def set_customer_id(self, customer_id):
        self.customer_id = customer_id


def create_new_customers():
    customers = randint(0, 2)
    return customers


async def insert_new_customer_to_queue(customer_queue_list, customers, store_closed):
    global customers_arrived
    counter = 1
    while counter <= 360:
        counter += 1
        customers_to_add = create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            min_queue = get_min_queue(customer_queue_list)
            await min_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        await asyncio.sleep(0.1)
    store_closed.set()


def get_min_queue(queue_list):
    queue_sizes = [q.qsize() for q in queue_list]
    return choice([q for q in queue_list if q.qsize() <= min(queue_sizes)])


async def work():
    done = asyncio.Event()
    customers = []
    workers = []
    jobs = []
    customer_queue_list = []

    for i in range(CONFIG["workers"]):
        worker = Worker()
        workers.append(worker)
        customer_queue_list.append(asyncio.Queue())

    q_stats = QueueStats(workers, customers)
    for i in range(len(workers)):
        jobs.append(workers[i].execute_job(customer_queue_list[i], done, q_stats))
    c = insert_new_customer_to_queue(customer_queue_list, customers, done)
    jobs.append(c)

    await asyncio.gather(*jobs)

    q_stats.report()


if __name__ == '__main__':
    asyncio.run(work())
