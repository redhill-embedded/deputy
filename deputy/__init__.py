import subprocess
from pathlib import Path
import pkg_resources

def get_git_version():
    """Retrieve the current Git tag version."""
    try:
        return subprocess.check_output(["git", "describe", "--tags"]).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        # Return None if git command fails, indicating non-git or no tags
        return None

def get_version():
    """Determine the version from either Git, a file, or package metadata."""
    # Check if installed in editable mode by checking for .git folder
    if (Path(__file__).parent / ".git").exists():
        git_version = get_git_version()
        if git_version:
            return git_version

    return pkg_resources.get_distribution("deputy").version

__version__ = get_version()