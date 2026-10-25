import shlex
from pathlib import Path
from commands import BUILTINS, run_builtin
from job_control import JobControl
from process_manager import launch_process
from piping import run_pipeline
from authentication import AuthenticationManager
from file_permissions import FilePermissionManager


class MiniShell:

    def __init__(self):
        self.running = True
        self.jobs = JobControl()
        
        # Set up simulated user accounts
        self.auth = AuthenticationManager()
        self.auth.add_user("admin", "AdminDemo2026!", "admin")
        self.auth.add_user("student", "StudentDemo2026!", "standard")

        # No user is authenticated initially
        self.current_user = None

        # Files managed by our simulated permission system
        self.permissions = FilePermissionManager()

        self.permissions.add_file(
            "system_config.txt",
            "System configuration: protected\n",
            owner="admin",
            others="r",
        )

        self.permissions.add_file(
            "student_notes.txt",
            "Student notes\n",
            owner="student",
            owner_rights="rw",
            others="r",
        )

        self.permissions.add_file(
            "admin_private.txt",
            "Confidential administrative information\n",
            owner="admin",
            owner_rights="rw",
            others="",
        )

    
    def handle_secure_command(self, args):
        command = args[0]
        user = self.current_user

        try:
            if command == "securels":
                if len(args) != 1:
                    raise ValueError("usage: securels")

                for path in sorted(self.permissions.rules):
                    print(path.name)

            elif command == "securecat":
                if len(args) != 2:
                    raise ValueError("usage: securecat <file>")

                print(
                    self.permissions.read_file(user, args[1]),
                    end="",
                )

            elif command == "securewrite":
                if len(args) < 3:
                    raise ValueError(
                        "usage: securewrite <file> <text>"
                    )

                self.permissions.write_file(
                    user, args[1], " ".join(args[2:]) + "\n"
                )
                print("File updated successfully.")

            elif command == "secureexec":
                if len(args) != 2:
                    raise ValueError("usage: secureexec <file>")

                print(self.permissions.execute_file(user, args[1]))

            elif command == "secureperms":
                if len(args) != 2:
                    raise ValueError("usage: secureperms <file>")

                print(
                    self.permissions.show_permissions(
                        user, args[1]
                    )
                )

        except (ValueError, PermissionError, OSError) as error:
            print(f"minishell: {error}")

        
    def check_protected_path(self, name):
        """Require secure* commands for the managed file area."""
        path = Path(name).expanduser().resolve()
        protected_root = self.permissions.root

        if path == protected_root or path.is_relative_to(protected_root):
            raise PermissionError(
                "Protected files must be accessed using "
                "securels, securecat, securewrite, "
                "secureexec, or secureperms."
            )



    def run(self):
        print("MiniShell - Unix-like Command Interpreter")
        # Require authentication before accepting commands
        try:
            self.current_user = self.auth.login()
        except (KeyboardInterrupt, EOFError):
            print("\nLogin cancelled.")
            return

        if self.current_user is None:
            print("Access denied. MiniShell will exit.")
            return
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

            # Handle piped commands
            if "|" in line:
                try:
                    run_pipeline(
                        line,
                        user=self.current_user,
                        permissions=self.permissions,
                    )
                except (
                    ValueError,
                    PermissionError,
                    OSError,
                    UnicodeError,
                ) as error:
                    print(f"minishell: {error}")
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

            # Execute simulated security commands
            if command in {
                "securels",
                "securecat",
                "securewrite",
                "secureexec",
                "secureperms",
            }:
                if background:
                    print("minishell: security commands cannot run in background")
                else:
                    self.handle_secure_command(args)
                continue

            # Execute built-in commands
            if command in BUILTINS:

                if background:
                    print(
                        "minishell: built-in commands "
                        "cannot run in background"
                    )

                else:
                    try:
                        # Restrict ordinary access to managed files.
                        if command in {
                            "cd", "ls", "cat",
                            "mkdir", "rmdir", "rm", "touch"
                        }:
                            if args[1:]:
                                self.check_protected_path(args[1])
                            elif command == "ls":
                                self.check_protected_path(".")
                        
                        run_builtin(args, self)
                   
                    except (PermissionError, OSError) as error:
                        print(f"minishell: {error}")
            # Execute external programs
            else:
                if self.current_user["role"] == "standard":
                    print(
                        "minishell: external programs are restricted "
                        "for standard users in this simulation."
                    )
                else:
                    launch_process(args, background, self)


if __name__ == "__main__":
    shell = MiniShell()
    shell.run()
