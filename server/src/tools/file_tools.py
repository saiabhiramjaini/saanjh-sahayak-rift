import os

BASE_REPO_PATH = "/repos"


def _resolve(session_id: str, relative_path: str) -> str:
    """
    Convert repo relative path to absolute EC2 path.
    """
    return os.path.join(BASE_REPO_PATH, session_id, relative_path)


def read_file(session_id: str, relative_path: str) -> str:
    path = _resolve(session_id, relative_path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(session_id: str, relative_path: str, content: str):
    path = _resolve(session_id, relative_path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
