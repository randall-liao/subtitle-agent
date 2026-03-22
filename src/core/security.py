import os
import shutil
from pathlib import Path


def is_safe_path(
    base_dir: os.PathLike[str] | str, target_path: os.PathLike[str] | str
) -> bool:
    """Check if the target path is safely within the base directory."""
    try:
        base = Path(base_dir).resolve(strict=True)
        target = Path(target_path).resolve()
        return base in target.parents or base == target
    except ValueError, FileNotFoundError, RuntimeError:
        return False


def safe_copy(
    src: os.PathLike[str] | str,
    dst: os.PathLike[str] | str,
    base_dir: os.PathLike[str] | str,
) -> None:
    """Safely copy a file to destination if it is within the base directory."""
    if not is_safe_path(base_dir, dst):
        raise ValueError(
            f"Destination path {dst} is not within safe base directory {base_dir}"
        )

    dst_path = Path(dst).resolve()
    base_path = Path(base_dir).resolve()
    manifest_path = base_path / ".subtitle_agent_files"

    if dst_path.exists():
        is_agent_created = False
        if manifest_path.exists():
            try:
                manifest_content = manifest_path.read_text().splitlines()
                if str(dst_path) in manifest_content:
                    is_agent_created = True
            except OSError:
                pass

        if not is_agent_created:
            raise PermissionError(f"Cannot overwrite {dst}: not created by the agent.")

    shutil.copy2(src, dst)

    try:
        with open(manifest_path, "a") as f:
            f.write(str(dst_path) + "\n")
    except OSError:
        pass
