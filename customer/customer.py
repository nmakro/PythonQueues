class Customer(object):
    def __init__(self):
        self.customer_id = 0
        self._waiting_time = 0.0
        self.time_started_waiting = 0.0
        self.time_in_queue = 0.0

    def set_time_in_queue(self, current_time):
        self.time_in_queue = (current_time - self.time_started_waiting) * 10.0

    def set_time_started_waiting(self, time_started):
        self.time_started_waiting = time_started

    def set_time_waited(self, current_time):
        self._waiting_time = (current_time - self.time_started_waiting) * 10.0

    def get_waiting_time(self):
        return self._waiting_time

    def set_customer_id(self, customer_id):
        self.customer_id = customer_id
