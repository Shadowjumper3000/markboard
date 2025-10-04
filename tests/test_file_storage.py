"""
Unit tests for FileStorage class in app.file_storage.
Covers file operations using a temporary directory.
"""

import os

import pytest
from app.file_storage import FileStorage


@pytest.fixture
def temp_storage_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("FILE_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def storage(temp_storage_dir):
    # Re-instantiate FileStorage to pick up new env var
    return FileStorage()


def test_generate_file_path_creates_subdir(storage):
    file_id = 1234
    filename = "test.txt"
    path = storage.generate_file_path(file_id, filename)
    # The storage fixture sets FILE_STORAGE_DIR, so we can check the prefix
    base_dir = storage.base_path
    assert path.startswith(base_dir)
    assert os.path.basename(path).endswith("test.txt")
    assert os.path.exists(os.path.dirname(path))


def test_save_and_read_file(storage):
    file_path = storage.generate_file_path(1, "foo.txt")
    content = "hello world"
    size, checksum = storage.save_file(file_path, content)
    assert size == len(content)
    assert isinstance(checksum, str)
    read = storage.read_file(file_path)
    assert read == content


def test_read_file_not_found(storage):
    with pytest.raises(FileNotFoundError):
        storage.read_file("/nonexistent/file.txt")


def test_delete_file(storage):
    file_path = storage.generate_file_path(2, "bar.txt")
    storage.save_file(file_path, "data")
    assert storage.delete_file(file_path) is True
    assert not os.path.exists(file_path)
    # Deleting again returns False
    assert storage.delete_file(file_path) is False


def test_move_file(storage):
    src = storage.generate_file_path(3, "move.txt")
    dst = storage.generate_file_path(4, "moved.txt")
    storage.save_file(src, "move me")
    assert storage.move_file(src, dst) is True
    assert os.path.exists(dst)
    assert not os.path.exists(src)


def test_copy_file(storage):
    src = storage.generate_file_path(5, "copy.txt")
    dst = storage.generate_file_path(6, "copied.txt")
    storage.save_file(src, "copy me")
    assert storage.copy_file(src, dst) is True
    assert os.path.exists(src)
    assert os.path.exists(dst)


def test_get_file_info(storage):
    file_path = storage.generate_file_path(7, "info.txt")
    storage.save_file(file_path, "info")
    info = storage.get_file_info(file_path)
    assert info["size"] == 4
    assert info["mime_type"].startswith("text/")
    assert isinstance(info["checksum"], str)
    assert info["modified"]
    # Nonexistent file
    assert storage.get_file_info("/nope.txt") is None


def test_file_exists(storage):
    file_path = storage.generate_file_path(8, "exists.txt")
    assert not storage.file_exists(file_path)
    storage.save_file(file_path, "exists")
    assert storage.file_exists(file_path)


def test_verify_file_integrity(storage):
    file_path = storage.generate_file_path(9, "integrity.txt")
    _, checksum = storage.save_file(file_path, "integrity")
    assert storage.verify_file_integrity(file_path, checksum) is True
    assert storage.verify_file_integrity(file_path, "badchecksum") is False
    assert storage.verify_file_integrity("/nope.txt", "irrelevant") is False


def test_cleanup_orphaned_files(storage):
    # Create two files, only one is referenced
    file1 = storage.generate_file_path(10, "orphan1.txt")
    file2 = storage.generate_file_path(11, "orphan2.txt")
    storage.save_file(file1, "keep")
    storage.save_file(file2, "delete")
    referenced = {file1}
    cleaned = storage.cleanup_orphaned_files(referenced)
    assert cleaned == 1
    assert os.path.exists(file1)
    assert not os.path.exists(file2)
