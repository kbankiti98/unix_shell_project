
import shlex

from commands import BUILTINS, run_builtin
from job_control import JobControl
from process_manager import launch_process


class MiniShell:

    def __init__(self):
        self.running = True
        self.jobs = JobControl()

    def run(self):
        print("MiniShell - Unix-like Command Interpreter")
        print("Type help to see available commands.")

        while self.running:

            # Check whether background processes changed state
            self.jobs.refresh()

            try:
                line = input("minishell> ").strip()

            except KeyboardInterrupt:
                print()
                continue

            except EOFError:
                print("\nExiting MiniShell.")
                break

            # Ignore empty commands
            if not line:
                continue

            # Separate the command from its arguments
            try:
                args = shlex.split(line)

            except ValueError as error:
                print(f"minishell: input: {error}")
                continue

            if not args:
                continue

            # Check for background execution
            background = args[-1] == "&"

            if background:
                args = args[:-1]

            if not args:
                print("minishell: missing command before &")
                continue

            command = args[0]

            # Execute built-in commands
            if command in BUILTINS:

                if background:
                    print(
                        "minishell: built-in commands "
                        "cannot run in background"
                    )

                else:
                    run_builtin(args, self)

            # Execute external programs
            else:
                launch_process(args, background, self)


if __name__ == "__main__":
    shell = MiniShell()
    shell.run()
