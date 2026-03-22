import os
from pathlib import Path

import pytest

from core.security import is_safe_path, safe_copy


def test_is_safe_path(tmp_path: Path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    safe_target = base_dir / "safe.srt"
    safe_target.write_text("safe content")

    unsafe_target = tmp_path / "unsafe.srt"
    unsafe_target.write_text("unsafe content")

    outside_target = base_dir / ".." / "outside.srt"

    assert is_safe_path(base_dir, safe_target) is True
    assert is_safe_path(base_dir, unsafe_target) is False
    assert is_safe_path(base_dir, outside_target) is False

    # 1. Absolute path traversal
    absolute_outside = Path("/etc/passwd")
    assert is_safe_path(base_dir, absolute_outside) is False

    # 2. Complex relative path
    complex_outside = base_dir / "sub" / ".." / ".." / "outside2.srt"
    assert is_safe_path(base_dir, complex_outside) is False

    # 3. Symlink tests
    safe_link = base_dir / "safe_link.srt"
    unsafe_link = base_dir / "unsafe_link.srt"

    os.symlink(safe_target, safe_link)
    os.symlink(unsafe_target, unsafe_link)

    assert is_safe_path(base_dir, safe_link) is True
    assert is_safe_path(base_dir, unsafe_link) is False

    # Mock Path.resolve to raise RuntimeError to test the exception block
    assert is_safe_path(base_dir, "\0invalid path") is False


def test_safe_copy(tmp_path: Path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    src = tmp_path / "src.srt"
    src.write_text("subtitle content")

    dst = base_dir / "dst.srt"
    safe_copy(src, dst, base_dir)
    assert dst.exists()
    assert dst.read_text() == "subtitle content"

    with pytest.raises(ValueError):
        safe_copy(src, tmp_path / "dst2.srt", base_dir)


def test_safe_copy_overwrite_protection(tmp_path: Path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    src = tmp_path / "src.srt"
    src.write_text("new content")

    dst = base_dir / "dst.srt"

    # Create the destination manually (not by the agent)
    dst.write_text("old content")

    # Expect PermissionError when trying to overwrite without manifest
    with pytest.raises(PermissionError):
        safe_copy(src, dst, base_dir)

    # Verify it was not overwritten
    assert dst.read_text() == "old content"

    # Now simulate the agent having created it previously
    manifest = base_dir / ".subtitle_agent_files"
    manifest.write_text(str(dst.resolve()) + "\n")

    # Now the copy should succeed
    safe_copy(src, dst, base_dir)
    assert dst.read_text() == "new content"


def test_safe_copy_creates_manifest(tmp_path: Path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    src = tmp_path / "src.srt"
    src.write_text("subtitle content")

    dst = base_dir / "new_dst.srt"
    safe_copy(src, dst, base_dir)

    manifest = base_dir / ".subtitle_agent_files"
    assert manifest.exists()
    assert str(dst.resolve()) in manifest.read_text().splitlines()
