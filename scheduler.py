
from dataclasses import dataclass
from typing import Optional


@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int

    def __post_init__(self):
        if self.arrival_time < 0:
            raise ValueError("Arrival time cannot be negative")

        if self.burst_time <= 0:
            raise ValueError("Burst time must be greater than zero")

        self.remaining_time = self.burst_time
        self.state = "New"
        self.first_run = None
        self.completion_time = None

    def record_start(self, current_time):
        if self.first_run is None:
            self.first_run = current_time

        self.state = "Running"

    def record_completion(self, current_time):
        self.remaining_time = 0
        self.completion_time = current_time
        self.state = "Done"

    def turnaround_time(self):
        if self.completion_time is None:
            return None

        return self.completion_time - self.arrival_time

    def waiting_time(self):
        turnaround = self.turnaround_time()

        if turnaround is None:
            return None

        return turnaround - self.burst_time

    def response_time(self):
        if self.first_run is None:
            return None

        return self.first_run - self.arrival_time
