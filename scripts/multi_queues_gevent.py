import gevent
from gevent import event
import queue
import time
from random import gauss, randint, choice
from queue_utils import QueueStats, CONFIG

WORKERS_NUM = 8
customers_arrived = 0


class Worker(object):
    def __init__(self):
        self._waiting_time = 0
        self._poll_queue_interval = 0.1
        self._total_execution_time = 0
        self._customers_served = 0
        self._execution_time = abs(gauss(CONFIG["execution_mean"], CONFIG["execution_deviation"]))

    def execute_job(self, customers_queue, done, q_stats):
        while not done.is_set() or not customers_queue.empty():
            q_stats.set_max_queue_size(customers_queue)
            try:
                customer = customers_queue.get_nowait()
            except queue.Empty:
                gevent.sleep(self._poll_queue_interval)
                self._waiting_time += self._poll_queue_interval
                continue
            self._customers_served += 1
            customer.set_waiting_time_in_worker(self._execution_time)
            customer.set_time_waited(time.time())
            gevent.sleep(self._execution_time)
            customer.total_waiting_time(self._execution_time)
            self._total_execution_time += self._execution_time

    def get_total_waiting_time(self):
        return self._waiting_time

    def get_total_working_time(self):
        return self._total_execution_time

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
    return randint(0, 2)


def insert_new_customer_to_queue(customer_queue_list, customers, store_closed):
    global customers_arrived
    counter = 1
    while counter <= 360:
        counter += 1
        customers_to_add = create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            min_queue = get_min_queue(customer_queue_list)
            min_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        gevent.sleep(0.1)
    store_closed.set()


def get_min_queue(queue_list):
    queue_sizes = [q.qsize() for q in queue_list]
    return choice([q for q in queue_list if q.qsize() <= min(queue_sizes)])


def work():
    customer_queue_list = []
    done = event.Event()
    customers = []
    workers = []
    jobs = []

    for i in range(CONFIG["workers"]):
        worker = Worker()
        workers.append(worker)
        customer_queue_list.append(queue.Queue())

    queue_stats = QueueStats(workers, customers)

    for i in range(CONFIG["workers"]):
        w = gevent.spawn(workers[i].execute_job, customer_queue_list[i], done, queue_stats)
        jobs.append(w)

    c = gevent.spawn(insert_new_customer_to_queue, customer_queue_list, customers, done)
    jobs.append(c)

    gevent.joinall(
        jobs
    )

    queue_stats.report()


if __name__ == '__main__':
    work()
