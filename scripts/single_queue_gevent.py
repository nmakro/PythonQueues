import gevent
from gevent import event
import queue
import time
import scripts.queue_utils as utils
from worker.worker import Worker
from customer.customer import Customer
from scripts.queue_utils import QueueStats, CONFIG


def insert_new_customer_to_queue(customer_queue, customers, store_closed):
    """Simulate customers entering the store for configured num of hours"""
    customers_arrived = 0
    counter = 1
    while counter <= CONFIG["minutes_store_is_open"]:

        customers_to_add = utils.create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            customer_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        # utils.report_customers(counter, customers_arrived)
        gevent.sleep(0.1)
        counter += 1
    store_closed.set()


def work():
    customer_queue = queue.Queue()
    done = event.Event()
    customers = []
    workers = []
    jobs = []

    for i in range(CONFIG["workers"]):
        worker = Worker()
        workers.append(worker)

    queue_stats = QueueStats(workers, customers)

    for i in range(CONFIG["workers"]):
        w = gevent.spawn(workers[i].execute_job, customer_queue, done, queue_stats)
        jobs.append(w)

    customer_job = gevent.spawn(insert_new_customer_to_queue, customer_queue, customers, done)
    jobs.append(customer_job)

    gevent.joinall(
        jobs
    )

    queue_stats.report()


if __name__ == '__main__':
    work()
