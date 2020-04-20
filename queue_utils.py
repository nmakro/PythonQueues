CONFIG = {
    "workers": 8,
    "execution_mean": 1.3,
    "execution_deviation": 0.5
}


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
        avg_waiting_time = sum([c.get_waiting_time() for c in self.customers]) / float(CONFIG["workers"])
        total_wait = sum(w.get_total_waiting_time() for w in self.workers)
        total_work = sum(w.get_total_working_time() for w in self.workers)
        print(f"Total customers arrived: {self.get_customers_served()}\n")
        print(f"Worker utilization: {round(100 - 100 * (total_wait / (total_wait + total_work)), 2)}%")
        print(f"Average waiting time per client: {round(avg_waiting_time, 2)}")
        print("Maximum queue size %d" % self.max_queue_size)
