import contextlib
import io
import tempfile
from pathlib import Path

from authentication import AuthenticationManager
from file_permissions import FilePermissionManager
from piping import run_pipeline


def check(name, test):
    try:
        test()
        print(f"PASS: {name}")
        return True
    except Exception as error:
        print(f"FAIL: {name} - {error}")
        return False


def expect_denied(action):
    try:
        action()
    except PermissionError:
        return
    raise AssertionError("Expected permission denial")


def expect_invalid(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("Expected invalid command")


def capture_pipeline(line, user, manager):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        run_pipeline(line, user=user, permissions=manager)
    return output.getvalue()


def main():
    auth = AuthenticationManager()
    auth.add_user("admin", "AdminDemo2026!", "admin")
    auth.add_user("student", "StudentDemo2026!", "standard")

    admin = {"username": "admin", "role": "admin"}
    student = {"username": "student", "role": "standard"}

    results = []

    results.append(check(
        "Admin authentication",
        lambda: assert_role(
            auth.authenticate("admin", "AdminDemo2026!"),
            "admin"
        )
    ))

    results.append(check(
        "Incorrect password rejected",
        lambda: assert_equal(
            auth.authenticate("student", "wrong"),
            None
        )
    ))

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manager = FilePermissionManager(root / "secure_files")

        manager.add_file(
            "system_config.txt",
            "System configuration\n",
            owner="admin",
            others="r",
        )
        manager.add_file(
            "admin_private.txt",
            "Confidential information\n",
            owner="admin",
            others="",
        )

        sample = root / "pipeline_test.txt"
        sample.write_text(
            "error zebra\ninfo message\nerror apple\n",
            encoding="utf-8",
        )

        results.append(check(
            "Student protected write denied",
            lambda: expect_denied(
                lambda: manager.write_file(
                    student, "system_config.txt", "not allowed"
                )
            )
        ))

        def admin_write():
            manager.write_file(
                admin, "system_config.txt", "authorized"
            )
            assert_equal(
                manager.read_file(admin, "system_config.txt"),
                "authorized"
            )

        results.append(check(
            "Admin protected write allowed",
            admin_write
        ))

        results.append(check(
            "Student private read denied",
            lambda: expect_denied(
                lambda: manager.read_file(
                    student, "admin_private.txt"
                )
            )
        ))

        def two_stage():
            output = capture_pipeline(
                f"cat {sample} | grep error",
                student,
                manager,
            )
            assert_equal(
                output,
                "error zebra\nerror apple\n"
            )

        results.append(check(
            "Two-stage pipeline",
            two_stage
        ))

        def three_stage():
            output = capture_pipeline(
                f"cat {sample} | grep error | sort",
                student,
                manager,
            )
            assert_equal(
                output,
                "error apple\nerror zebra\n"
            )

        results.append(check(
            "Three-stage pipeline",
            three_stage
        ))

        results.append(check(
            "Protected pipeline denied",
            lambda: expect_denied(
                lambda: capture_pipeline(
                    f"cat {root / 'secure_files' / 'admin_private.txt'} "
                    "| grep Confidential",
                    student,
                    manager,
                )
            )
        ))

        results.append(check(
            "Unsupported pipeline command rejected",
            lambda: expect_invalid(
                lambda: capture_pipeline(
                    "python3 --version | sort",
                    student,
                    manager,
                )
            )
        ))

        def persistence():
            manager.write_file(
                admin, "system_config.txt", "persistent update"
            )
            second_manager = FilePermissionManager(
                root / "secure_files"
            )
            second_manager.add_file(
                "system_config.txt",
                "original content",
                owner="admin",
                others="r",
            )
            assert_equal(
                second_manager.read_file(admin, "system_config.txt"),
                "persistent update"
            )

        results.append(check(
            "File persistence",
            persistence
        ))

    print("--------------------------------")
    print(f"{sum(results)} of {len(results)} Deliverable 4 tests passed")


def assert_equal(actual, expected):
    assert actual == expected, (
        f"Expected {expected!r}, got {actual!r}"
    )


def assert_role(user, expected):
    assert user is not None
    assert_equal(user["role"], expected)


if __name__ == "__main__":
    main()
