
import os
import signal


class JobControl:

    def __init__(self):
        self.jobs = {}
        self.next_id = 1

    # Register a process in the job table
    def add(self, process, command):

        job_id = self.next_id
        self.next_id += 1

        self.jobs[job_id] = {
            "process": process,
            "command": command,
            "status": "Running"
        }

        return job_id

    # Update the current state of a process
    def update_status(self, job, status):

        process = job["process"]

        if os.WIFSTOPPED(status):
            job["status"] = "Stopped"

        elif os.WIFCONTINUED(status):
            job["status"] = "Running"

        elif os.WIFEXITED(status):
            process.returncode = os.WEXITSTATUS(status)
            job["status"] = "Done"

        elif os.WIFSIGNALED(status):
            process.returncode = -os.WTERMSIG(status)
            job["status"] = "Terminated"

    # Check running and stopped processes for changes
    def refresh(self):

        for job in self.jobs.values():

            if job["status"] in ("Done", "Terminated"):
                continue

            while True:

                try:
                    pid, status = os.waitpid(
                        job["process"].pid,
                        os.WNOHANG |
                        os.WUNTRACED |
                        os.WCONTINUED
                    )

                except ChildProcessError:
                    break

                if pid == 0:
                    break

                self.update_status(job, status)

                if job["status"] in ("Done", "Terminated"):
                    break

    # Find a registered job by its ID
    def find(self, value):

        try:
            job_id = int(value.lstrip("%"))

        except ValueError:
            raise ValueError(
                "job ID must be a number"
            )

        if job_id <= 0:
            raise ValueError(
                "job ID must be positive"
            )

        if job_id not in self.jobs:
            raise ValueError(
                f"job {job_id} does not exist"
            )

        return job_id, self.jobs[job_id]

    # Display all registered jobs
    def show(self):

        self.refresh()

        if not self.jobs:
            print("No jobs recorded.")
            return

        for job_id, job in self.jobs.items():

            print(
                f"[{job_id}] "
                f"{job['status']:<10} "
                f"PID={job['process'].pid} "
                f"{job['command']}"
            )

    # Wait for a foreground process
    def wait_foreground(self, job_id):

        job = self.jobs[job_id]
        process = job["process"]

        while job["status"] == "Running":

            try:
                pid, status = os.waitpid(
                    process.pid,
                    os.WUNTRACED
                )

            except KeyboardInterrupt:

                # Forward Ctrl+C to the child process group
                try:
                    os.killpg(
                        process.pid,
                        signal.SIGINT
                    )

                except ProcessLookupError:
                    pass

                continue

            except ChildProcessError:
                break

            if pid == process.pid:
                self.update_status(job, status)

        if job["status"] == "Stopped":

            print(
                f"[{job_id}] Stopped: "
                f"{job['command']}"
            )

        elif job["status"] in ("Done", "Terminated"):

            del self.jobs[job_id]

    # Bring a background job to the foreground
    def foreground(self, value):

        self.refresh()

        job_id, job = self.find(value)

        if job["status"] in ("Done", "Terminated"):

            print(
                f"[{job_id}] Already "
                f"{job['status'].lower()}"
            )
            return

        if job["status"] == "Stopped":

            os.killpg(
                job["process"].pid,
                signal.SIGCONT
            )

            job["status"] = "Running"

        print(
            f"Foreground: [{job_id}] "
            f"{job['command']}"
        )

        self.wait_foreground(job_id)

    # Resume a stopped job in the background
    def background(self, value):

        self.refresh()

        job_id, job = self.find(value)

        if job["status"] != "Stopped":

            raise ValueError(
                f"job {job_id} is not stopped"
            )

        os.killpg(
            job["process"].pid,
            signal.SIGCONT
        )

        job["status"] = "Running"

        print(
            f"[{job_id}] Resumed in background: "
            f"{job['command']}"
        )

    # Stop a running job
    def stop(self, value):

        self.refresh()

        job_id, job = self.find(value)

        if job["status"] != "Running":

            raise ValueError(
                f"job {job_id} is not running"
            )

        os.killpg(
            job["process"].pid,
            signal.SIGSTOP
        )

        job["status"] = "Stopped"

        print(
            f"[{job_id}] Stopped: "
            f"{job['command']}"
        )
