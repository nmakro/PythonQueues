import gevent
from gevent.event import Event
import queue
import time
from random import gauss, randint

CUSTOMERS_ARRIVED = 0
WORKERS_NUM = 8
FINISHED = False
MAX_QUEUE_SIZE = 0


class Worker(object):
    def __init__(self):
        self._execution_time = 0
        self.total_execution_time = 0
        self.client_served = 0

    def execute_job(self, client_queue):
        global FINISHED
        global MAX_QUEUE_SIZE
        while not FINISHED or not client_queue.empty():
            try:
                if client_queue.qsize() > MAX_QUEUE_SIZE:
                    MAX_QUEUE_SIZE = client_queue.qsize()
                client = client_queue.get_nowait()
                # print("Current queue size: %d" % client_queue.qsize())
            except queue.Empty:
                gevent.sleep(0.1)
                if FINISHED and client_queue.qsize() == 0:
                    return
                continue
            self._execution_time = abs(gauss(0.51, 0.20))
            client.set_waiting_time_in_worker(self._execution_time)
            self.client_served += 1
            client.set_time_waited(time.time())
            # print("Serving customer %d " % client.client_id)
            gevent.sleep(self._execution_time)
            client.total_waiting_time(self._execution_time)
            self.total_execution_time += self._execution_time


class Client(object):
    def __init__(self):
        self.client_id = 0
        self.waiting_time = 0.0
        self.waiting_time_in_worker = 0.0
        self.time_started_waiting = 0.0

    def set_waiting_time_in_worker(self, time_in_worker):
        self.waiting_time_in_worker = time_in_worker

    def set_time_started_waiting(self, time_started):
        self.time_started_waiting = time_started

    def set_time_waited(self, current_time):
        self.waiting_time = current_time - self.time_started_waiting

    def total_waiting_time(self, time_waited_in_job):
        self.waiting_time += time_waited_in_job

    def get_waiting_time(self):
        return self.waiting_time

    def set_client_id(self, client_id):
        self.client_id = client_id


def create_new_clients():
    new_clients = randint(0, 3)
    return new_clients


def insert_new_client_to_queue(clients_queue, client_list):
    global CUSTOMERS_ARRIVED
    counter = 1
    while counter <= 360:
        counter += 1
        clients_to_add = create_new_clients()
        CUSTOMERS_ARRIVED += clients_to_add
        for i in range(clients_to_add):
            client = Client()
            clients_queue.put(client)
            client.set_time_started_waiting(time.time())
            client_list.append(client)
            client.set_client_id(client_list.index(client))
        if counter % 60 == 0:
                print("Minutes passed: %d" % counter)
                print("Customers arrived the %d hour: %d" % (counter / 60, CUSTOMERS_ARRIVED))

        gevent.sleep(0.1)
    global FINISHED
    FINISHED = True


def work(client_queue, client_list):
    worker_list = []
    jobs = []

    for i in range(WORKERS_NUM):
        worker = Worker()
        worker_list.append(worker)

    for i in range(len(worker_list)):
        w = gevent.spawn(worker_list[i].execute_job, client_queue)
        jobs.append(w)

    client_job = gevent.spawn(insert_new_client_to_queue, client_queue, client_list)
    jobs.append(client_job)

    gevent.joinall(
        jobs
    )
    sum_waiting_time = 0.0
    sum_waiting_time_in_worker = 0.0
    for client in clients:
        sum_waiting_time += client.get_waiting_time()
        sum_waiting_time_in_worker += client.waiting_time_in_worker

    print("Total customers arrived: %d\n" % CUSTOMERS_ARRIVED)
    avg = sum_waiting_time / float(len(clients))
    avg_in_worker = sum_waiting_time_in_worker / float(len(clients))
    print("Average waiting time per client: %f\n" % avg)
    print("Average waiting time per client in worker: %f'\n" % avg_in_worker)

    for worker in range(len(worker_list)):
        print("Worker %d total working time %f" % (worker, worker_list[worker].total_execution_time))
        print("Number of customers served : %d" % worker_list[worker].client_served)

    print("Maximum queue size %d" % MAX_QUEUE_SIZE)


if __name__ == '__main__':
    client_queue = queue.Queue()
    clients = []

    work(client_queue, clients)
