
from collections import deque
import time

from scheduler import Process


def round_robin(processes, quantum, delay=0):

    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero")

    if delay < 0:
        raise ValueError("Delay cannot be negative")

    if not processes:
        print("No processes to schedule.")
        return []

    # Create fresh copies so repeated tests use the same workload
    jobs = [
        Process(p.pid, p.arrival_time, p.burst_time, p.priority)
        for p in processes
    ]

    jobs.sort(key=lambda p: p.arrival_time)

    ready_queue = deque()
    current_time = 0
    next_job = 0
    completed = 0
    timeline = []

    print(f"\nRound-Robin Scheduling | Quantum: {quantum}")

    while completed < len(jobs):

        # Add processes that have arrived
        while (
            next_job < len(jobs)
            and jobs[next_job].arrival_time <= current_time
        ):
            job = jobs[next_job]
            job.state = "Ready"
            ready_queue.append(job)

            print(f"Time {current_time}: P{job.pid} entered the ready queue")
            next_job += 1

        if not ready_queue:
            current_time = jobs[next_job].arrival_time
            continue

        # Select the next process
        job = ready_queue.popleft()

        job.record_start(current_time)

        run_time = min(quantum, job.remaining_time)

        start_time = current_time
        end_time = current_time + run_time

        print(
            f"Time {start_time}-{end_time}: "
            f"P{job.pid} running"
        )

        if delay:
            time.sleep(run_time * delay)

        job.remaining_time -= run_time
        current_time = end_time

        timeline.append(
            (job.pid, start_time, end_time)
        )

        # Add arrivals before requeuing the current process
        while (
            next_job < len(jobs)
            and jobs[next_job].arrival_time <= current_time
        ):
            new_job = jobs[next_job]
            new_job.state = "Ready"
            ready_queue.append(new_job)

            print(
                f"Time {new_job.arrival_time}: "
                f"P{new_job.pid} entered the ready queue"
            )

            next_job += 1

        if job.remaining_time == 0:
            job.record_completion(current_time)
            completed += 1

            print(f"Time {current_time}: P{job.pid} completed")

        else:
            job.state = "Ready"
            ready_queue.append(job)

            print(
                f"Time {current_time}: P{job.pid} "
                f"requeued ({job.remaining_time} remaining)"
            )

    print("\nScheduling Results")
    print("PID  Waiting  Turnaround  Response")

    for job in sorted(jobs, key=lambda p: p.pid):
        print(
            f"P{job.pid:<3} "
            f"{job.waiting_time():<8} "
            f"{job.turnaround_time():<11} "
            f"{job.response_time()}"
        )

    average_waiting = sum(
        job.waiting_time() for job in jobs
    ) / len(jobs)

    average_turnaround = sum(
        job.turnaround_time() for job in jobs
    ) / len(jobs)

    average_response = sum(
        job.response_time() for job in jobs
    ) / len(jobs)

    print(f"\nAverage waiting time: {average_waiting:.2f}")
    print(f"Average turnaround time: {average_turnaround:.2f}")
    print(f"Average response time: {average_response:.2f}")

    return jobs


if __name__ == "__main__":

    processes = [
        Process(1, 0, 5, 2),
        Process(2, 0, 3, 1),
        Process(3, 0, 4, 3)
    ]

    round_robin(processes, quantum=2)