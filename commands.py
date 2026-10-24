
import os
import signal


# Commands handled directly by MiniShell
BUILTINS = {
    "cd", "pwd", "exit", "echo", "clear",
    "ls", "cat", "mkdir", "rmdir", "rm",
    "touch", "kill", "jobs", "fg", "bg",
    "stop", "help"
}


# Check whether a command has the required arguments
def check_arguments(values, count, usage):
    if len(values) != count:
        raise ValueError(f"usage: {usage}")


# Execute built-in shell commands
def run_builtin(args, shell):

    command = args[0]
    values = args[1:]

    try:

        # Change the working directory
        if command == "cd":
            if len(values) > 1:
                raise ValueError("usage: cd [directory]")

            directory = values[0] if values else "~"
            os.chdir(os.path.expanduser(directory))

        # Display the current directory
        elif command == "pwd":
            check_arguments(values, 0, "pwd")
            print(os.getcwd())

        # Exit MiniShell
        elif command == "exit":
            check_arguments(values, 0, "exit")
            shell.running = False
            print("Exiting MiniShell.")

        # Display text
        elif command == "echo":
            print(" ".join(values))

        # Clear the terminal screen
        elif command == "clear":
            check_arguments(values, 0, "clear")
            print("\033[2J\033[H", end="", flush=True)

        # List files and directories
        elif command == "ls":
            if len(values) > 1:
                raise ValueError("usage: ls [directory]")

            directory = values[0] if values else "."

            for filename in sorted(os.listdir(directory)):
                print(filename)

        # Display the contents of a file
        elif command == "cat":
            check_arguments(values, 1, "cat <filename>")

            with open(values[0], "r", encoding="utf-8") as file:
                print(file.read(), end="")

        # Create a directory
        elif command == "mkdir":
            check_arguments(values, 1, "mkdir <directory>")
            os.mkdir(values[0])

        # Remove an empty directory
        elif command == "rmdir":
            check_arguments(values, 1, "rmdir <directory>")
            os.rmdir(values[0])

        # Delete a file
        elif command == "rm":
            check_arguments(values, 1, "rm <filename>")
            os.remove(values[0])

        # Create a file or update its timestamp
        elif command == "touch":
            check_arguments(values, 1, "touch <filename>")

            with open(values[0], "a", encoding="utf-8"):
                pass

            os.utime(values[0], None)

        # Terminate a process using its PID
        elif command == "kill":
            check_arguments(values, 1, "kill <pid>")

            pid = int(values[0])

            if pid <= 0:
                raise ValueError("PID must be positive")

            os.kill(pid, signal.SIGTERM)
            print(f"Termination signal sent to PID {pid}")

        # Display background jobs
        elif command == "jobs":
            check_arguments(values, 0, "jobs")
            shell.jobs.show()

        # Bring a job to the foreground
        elif command == "fg":
            check_arguments(values, 1, "fg <job_id>")
            shell.jobs.foreground(values[0])

        # Resume a stopped job in the background
        elif command == "bg":
            check_arguments(values, 1, "bg <job_id>")
            shell.jobs.background(values[0])

        # Stop a running job
        elif command == "stop":
            check_arguments(values, 1, "stop <job_id>")
            shell.jobs.stop(values[0])

        # Display available commands
        elif command == "help":
            check_arguments(values, 0, "help")

            print("\nMiniShell - Available Commands")
            print("--------------------------------")
            print("cd       Change directory")
            print("pwd      Display current directory")
            print("exit     Exit MiniShell")
            print("echo     Display text")
            print("clear    Clear terminal")
            print("ls       List files and directories")
            print("cat      Display file contents")
            print("mkdir    Create directory")
            print("rmdir    Remove empty directory")
            print("rm       Delete file")
            print("touch    Create or update file")
            print("kill     Terminate process by PID")
            print("jobs     Display jobs")
            print("fg       Bring job to foreground")
            print("bg       Resume stopped background job")
            print("stop     Stop a running job")
            print("help     Display available commands")

            print("\nProcess Execution Examples:")
            print("Foreground: sleep 10")
            print("Background: sleep 30 &")
            print()

    # Handle errors without crashing the shell
    except (OSError, ValueError, UnicodeError) as error:
        print(f"minishell: {command}: {error}")
