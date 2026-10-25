
import os
import subprocess
import sys
import tempfile


# Location of the main shell program
SHELL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "minishell.py"
)


def run_test(name, commands, expected):
    with tempfile.TemporaryDirectory() as folder:
        try: 
            # Authenticate before running the original test commands.
            # The admin role preserves external-process test coverage.
            test_input = "\n".join(
                ["admin", "AdminDemo2026!"] + commands + ["exit"]
            ) + "\n"

            result = subprocess.run(
                [sys.executable, SHELL_PATH],
                input=test_input,
                text=True,
                capture_output=True,
                cwd=folder,
                timeout=15,
            )


            output = result.stdout + result.stderr

            passed = (
                result.returncode == 0
                and all(text in output for text in expected)
            )

            if passed:
                print(f"PASS: {name}")
            else:
                print(f"FAIL: {name}")
                print(output)

            return passed

        except subprocess.TimeoutExpired:
            print(f"FAIL: {name} - test timed out")
            return False


def main():
    print("MiniShell Test Results")
    print("----------------------")

    tests = [
        (
            "Basic commands",
            ["pwd", "echo Operating Systems"],
            ["Operating Systems"]
        ),
        (
            "Directory commands",
            ["mkdir assignments", "cd assignments", "pwd"],
            ["assignments"]
        ),
        (
            "File commands",
            ["touch notes.txt", "ls", "rm notes.txt"],
            ["notes.txt"]
        ),
        (
            "Invalid command",
            ["notacommand"],
            ["command not found"]
        ),
        (
            "Missing directory",
            ["cd missing_folder"],
            ["No such file or directory"]
        ),
        (
            "Foreground process",
            ["sleep 1", "echo Finished"],
            ["Finished"]
        )
    ]

    results = []

    for name, commands, expected in tests:
        results.append(
            run_test(name, commands, expected)
        )

    print("----------------------")
    print(f"{sum(results)} of {len(results)} tests passed")


if __name__ == "__main__":
    main()
