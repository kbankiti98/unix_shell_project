
import subprocess


def launch_process(args, background, shell):

    try:
        # Start the external program
        process = subprocess.Popen(
            args,
            start_new_session=True
        )

    except FileNotFoundError:
        print(f"minishell: {args[0]}: command not found")
        return

    except OSError as error:
        print(f"minishell: {args[0]}: {error}")
        return

    # Register the process in the job table
    job_id = shell.jobs.add(
        process,
        " ".join(args)
    )

    if background:

        # Let the shell accept another command immediately
        print(
            f"[{job_id}] PID={process.pid} "
            f"Running: {' '.join(args)}"
        )

    else:

        # Wait until the foreground process finishes
        # or enters a stopped state
        shell.jobs.wait_foreground(job_id)
