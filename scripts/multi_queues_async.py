import asyncio
import time
import scripts.queue_utils as utils
from customer.customer import Customer
from worker.worker import AsyncWorker
from scripts.queue_utils import QueueStats, CONFIG


async def insert_new_customer_to_queue(customer_queue_list, customers, store_closed):
    """Simulate customers entering the store for configured num of minutes"""
    customers_arrived = 0
    counter = 1
    while counter <= 360:
        customers_to_add = utils.create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            min_queue = utils.get_min_queue(customer_queue_list)
            await min_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        # utils.report_customers(counter, customers_arrived)
        await asyncio.sleep(0.1)
        counter += 1
    store_closed.set()


async def work():
    done = asyncio.Event()
    customers = []
    workers = []
    jobs = []
    customer_queue_list = []

    for i in range(CONFIG["workers"]):
        worker = AsyncWorker()
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
