import asyncio
import time
from worker.worker import AsyncWorker
from customer.customer import Customer
import scripts.queue_utils as utils
from scripts.queue_utils import QueueStats, CONFIG


async def insert_new_customer_to_queue(customers_queue, customers, store_closed):
    """Simulate customers entering the store for configured num of hours"""
    customers_arrived = 0
    counter = 1
    while counter <= CONFIG["minutes_store_is_open"]:
        """Every min some random number of customers arrive"""
        customers_to_add = utils.create_new_customers()
        customers_arrived += customers_to_add
        for i in range(customers_to_add):
            customer = Customer()
            await customers_queue.put(customer)
            customer.set_time_started_waiting(time.time())
            customers.append(customer)
            customer.set_customer_id(customers.index(customer))

        # utils.report_customers(counter, customers_arrived)
        await asyncio.sleep(0.1)
        counter += 1
    store_closed.set()
    customers_queue.task_done()


async def work():
    q = asyncio.Queue()
    done = asyncio.Event()
    customers = []
    workers = []
    jobs = []

    for i in range(CONFIG["workers"]):
        worker = AsyncWorker()
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
