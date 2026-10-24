
import io
from contextlib import redirect_stdout

from scheduler import Process
from round_robin import round_robin
from priority_scheduler import priority_scheduling


def run_quietly(function, *args, **kwargs):
    output = io.StringIO()

    with redirect_stdout(output):
        result = function(*args, **kwargs)

    return result, output.getvalue()


def check_results(name, actual, expected):
    if actual == expected:
        print(f"PASS: {name}")
        return True

    print(f"FAIL: {name}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    return False


def get_metrics(jobs):
    return {
        job.pid: (
            job.waiting_time(),
            job.turnaround_time(),
            job.response_time()
        )
        for job in jobs
    }


def main():
    passed = 0
    total = 0

    workload = [
        Process(1, 0, 6, 3),
        Process(2, 2, 3, 1),
        Process(3, 3, 2, 2)
    ]

    # Round-Robin scheduling and metrics
    rr_jobs, rr_output = run_quietly(
        round_robin, workload, 2
    )

    total += 1
    passed += check_results(
        "Round-Robin metrics",
        get_metrics(rr_jobs),
        {
            1: (5, 11, 0),
            2: (4, 7, 0),
            3: (3, 5, 3)
        }
    )

    total += 1
    passed += check_results(
        "Round-Robin quantum",
        "Quantum: 2" in rr_output,
        True
    )

    # Priority scheduling and metrics
    priority_jobs, priority_output = run_quietly(
        priority_scheduling, workload
    )

    total += 1
    passed += check_results(
        "Priority metrics",
        get_metrics(priority_jobs),
        {
            1: (5, 11, 0),
            2: (0, 3, 0),
            3: (2, 4, 2)
        }
    )

    total += 1
    passed += check_results(
        "Priority preemption",
        "P1 preempted by P2" in priority_output,
        True
    )

    # Test FCFS behavior with equal priorities
    tie_workload = [
        Process(1, 0, 3, 2),
        Process(2, 0, 2, 2),
        Process(3, 1, 2, 1)
    ]

    tie_jobs, tie_output = run_quietly(
        priority_scheduling, tie_workload
    )

    total += 1
    passed += check_results(
        "FCFS tie-breaking",
        tie_output.index("P1 completed")
        < tie_output.index("P2 started running"),
        True
    )

    # Invalid quantum should raise ValueError
    total += 1

    try:
        run_quietly(round_robin, workload, 0)
        rejected = False
    except ValueError:
        rejected = True

    passed += check_results(
        "Invalid quantum rejected",
        rejected,
        True
    )

    print(f"\n{passed} of {total} scheduling tests passed")


if __name__ == "__main__":
    main()
