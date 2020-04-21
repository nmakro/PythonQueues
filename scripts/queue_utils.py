from random import randint, gauss, choice

CONFIG = {
    "workers": 9,
    "execution_mean": 1.2,
    "execution_deviation": 0.5,
    "poll_queue_interval": 0.05,
    "max_customers_per_interval": 3,
    "minutes_store_is_open": 360
}


def create_new_customers():
    customers = randint(0, CONFIG["max_customers_per_interval"])
    return customers


def get_execution_time():
    return abs(gauss(CONFIG["execution_mean"], CONFIG["execution_deviation"]))


def report_customers(counter, customers_arrived):
    if counter % 60 == 0:
        print(f"After {counter} minutes: {customers_arrived} customers have arrived.")


def get_min_queue(queue_list):
    queue_sizes = [q.qsize() for q in queue_list]
    return choice([q for q in queue_list if q.qsize() <= min(queue_sizes)])


class QueueStats(object):
    def __init__(self, workers, customers):
        self.workers = workers
        self.customers = customers
        self.max_queue_size = 0

    def set_max_queue_size(self, queue):
        size = queue.qsize()
        if size > self.max_queue_size:
            self.max_queue_size = size

    def get_customers_served(self):
        return sum(w.get_total_customers_served() for w in self.workers)

    def report(self):
        avg_waiting_time = sum([c.get_waiting_time() for c in self.customers]) / len(self.customers)
        total_wait = sum(w.get_total_waiting_time() for w in self.workers)
        total_work = sum(w.get_total_working_time() for w in self.workers)
        print(f"\n\nTotal customers arrived: {self.get_customers_served()}\n")
        print(f"Worker utilization: {round(100 - 100 * (total_wait / (total_wait + total_work)), 2)}%")
        print(f"Average waiting time per client: {round(avg_waiting_time, 2)} minutes")
        print(f"Maximum queue size: {self.max_queue_size}")
