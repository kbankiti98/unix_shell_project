
import heapq
import time

from scheduler import Process


def priority_scheduling(processes, delay=0):

    if delay < 0:
        raise ValueError("Delay cannot be negative")

    if not processes:
        print("No processes to schedule.")
        return []

    # Create fresh copies for each simulation
    jobs = [
        Process(p.pid, p.arrival_time, p.burst_time, p.priority)
        for p in processes
    ]

    # Python's sort preserves input order for equal arrival times
    jobs.sort(key=lambda p: p.arrival_time)

    ready_queue = []
    current_time = 0
    next_job = 0
    completed = 0
    arrival_order = 0
    running = None

    print("\nPreemptive Priority Scheduling")
    print("Lower priority number means higher priority.")

    while completed < len(jobs):

        # Add processes that have arrived
        while (
            next_job < len(jobs)
            and jobs[next_job].arrival_time <= current_time
        ):
            job = jobs[next_job]
            job.state = "Ready"

            heapq.heappush(
                ready_queue,
                (job.priority, arrival_order, job)
            )

            print(
                f"Time {job.arrival_time}: "
                f"P{job.pid} arrived "
                f"(priority {job.priority})"
            )

            arrival_order += 1
            next_job += 1

        # Select the highest-priority ready process
        if running is None:

            if not ready_queue:
                current_time = jobs[next_job].arrival_time
                continue

            _, _, running = heapq.heappop(ready_queue)
            running.record_start(current_time)

            print(
                f"Time {current_time}: "
                f"P{running.pid} started running"
            )

        # Execute until completion or the next arrival
        next_arrival = (
            jobs[next_job].arrival_time
            if next_job < len(jobs)
            else float("inf")
        )

        run_time = min(
            running.remaining_time,
            next_arrival - current_time
        )

        start_time = current_time

        if delay:
            time.sleep(run_time * delay)

        running.remaining_time -= run_time
        current_time += run_time

        print(
            f"Time {start_time}-{current_time}: "
            f"P{running.pid} executed"
        )

        # Add any newly arrived processes
        while (
            next_job < len(jobs)
            and jobs[next_job].arrival_time <= current_time
        ):
            job = jobs[next_job]
            job.state = "Ready"

            heapq.heappush(
                ready_queue,
                (job.priority, arrival_order, job)
            )

            print(
                f"Time {job.arrival_time}: "
                f"P{job.pid} arrived "
                f"(priority {job.priority})"
            )

            arrival_order += 1
            next_job += 1

        # Check completion first
        if running.remaining_time == 0:

            running.record_completion(current_time)

            print(
                f"Time {current_time}: "
                f"P{running.pid} completed"
            )

            completed += 1
            running = None

        # Preempt only for a strictly higher priority
        elif ready_queue and ready_queue[0][0] < running.priority:

            print(
                f"Time {current_time}: "
                f"P{running.pid} preempted by "
                f"P{ready_queue[0][2].pid}"
            )

            running.state = "Ready"

            # Preserve the original arrival order for FCFS ties
            original_order = jobs.index(running)

            heapq.heappush(
                ready_queue,
                (running.priority, original_order, running)
            )

            running = None

    print("\nScheduling Results")
    print("PID  Priority  Waiting  Turnaround  Response")

    for job in sorted(jobs, key=lambda p: p.pid):
        print(
            f"P{job.pid:<3} "
            f"{job.priority:<9} "
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
        Process(1, 0, 6, 3),
        Process(2, 2, 3, 1),
        Process(3, 3, 2, 2)
    ]

    priority_scheduling(processes)
