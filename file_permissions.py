
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileRule:
    owner: str
    admin_permissions: str
    owner_permissions: str
    other_permissions: str


class FilePermissionManager:
    def __init__(self, root="secure_files"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.rules = {}

    def add_file(self, name, content, owner,
                 admin="rwx", owner_rights="rw", others="r"):
        path = self._resolve(name)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize simulated file contents.
        if not path.exists():
            path.write_text(content, encoding="utf-8")

        self.rules[path] = FileRule(
            owner=owner,
            admin_permissions=admin,
            owner_permissions=owner_rights,
            other_permissions=others,
        )

    def _resolve(self, name):
        path = (self.root / name).resolve()

        if not path.is_relative_to(self.root) or path == self.root:
            raise ValueError("Access outside secure_files is not allowed.")

        return path

    def check(self, user, name, permission):
        if user is None:
            raise PermissionError("Login required.")

        if permission not in ("r", "w", "x"):
            raise ValueError("Invalid permission.")

        path = self._resolve(name)
        rule = self.rules.get(path)

        if rule is None:
            raise PermissionError("File is not registered.")

        if user["role"] == "admin":
            allowed = permission in rule.admin_permissions
        elif user["username"] == rule.owner:
            allowed = permission in rule.owner_permissions
        else:
            allowed = permission in rule.other_permissions

        if not allowed:
            raise PermissionError(
                f"Access denied: {permission} permission required "
                f"for {name}."
            )

        return path

    def read_file(self, user, name):
        path = self.check(user, name, "r")
        return path.read_text(encoding="utf-8")

    def write_file(self, user, name, content):
        path = self.check(user, name, "w")
        path.write_text(content, encoding="utf-8")

    def execute_file(self, user, name):
        path = self.check(user, name, "x")
        return f"Simulated execution permitted: {path.name}"

    def show_permissions(self, user, name):
        path = self._resolve(name)
        rule = self.rules.get(path)

        if rule is None:
            raise PermissionError("File is not registered.")

        return (
            f"{path.name}: owner={rule.owner}, "
            f"admin={rule.admin_permissions}, "
            f"owner={rule.owner_permissions}, "
            f"others={rule.other_permissions}"
        )
