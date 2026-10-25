
import os
import shlex
from pathlib import Path


def run_pipeline(command_line, user=None, permissions=None):
    """Execute supported pipeline stages with file permission checks."""

    if user is None or permissions is None:
        raise PermissionError("Login and permissions are required.")

    stages = command_line.split("|")

    if len(stages) < 2:
        raise ValueError("A pipeline requires at least two commands.")

    previous_output = ""

    for stage in stages:
        arguments = shlex.split(stage.strip())

        if not arguments:
            raise ValueError("A pipeline cannot contain an empty command.")

        command = arguments[0]

        if command == "ls":
            if len(arguments) != 1:
                raise ValueError("Pipeline usage: ls")

            names = sorted(
                name for name in os.listdir(".")
                if name != permissions.root.name
            )
            previous_output = "\n".join(names)
            if names:
                previous_output += "\n"

        elif command == "cat":
            if len(arguments) != 2:
                raise ValueError("Pipeline usage: cat <filename>")

            path = Path(arguments[1]).expanduser().resolve()

            if path == permissions.root:
                raise PermissionError("Cannot read protected directory.")

            if path.is_relative_to(permissions.root):
                relative_name = str(
                    path.relative_to(permissions.root)
                )
                previous_output = permissions.read_file(
                    user, relative_name
                )
            else:
                previous_output = path.read_text(
                    encoding="utf-8"
                )

        elif command == "grep":
            if len(arguments) != 2:
                raise ValueError("Pipeline usage: grep <text>")

            previous_output = "".join(
                line
                for line in previous_output.splitlines(keepends=True)
                if arguments[1] in line
            )

        elif command == "sort":
            if len(arguments) != 1:
                raise ValueError("Pipeline usage: sort")

            lines = previous_output.splitlines()
            previous_output = "\n".join(sorted(lines))

            if lines:
                previous_output += "\n"

        elif command == "echo":
            previous_output = " ".join(arguments[1:]) + "\n"

        else:
            raise ValueError(
                f"Unsupported pipeline command: {command}"
            )

    if previous_output:
        print(previous_output, end="")