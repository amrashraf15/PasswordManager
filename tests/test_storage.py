from pathlib import Path
from vault.storage import write_json, read_json

def run_storage_tests():
    test_path = Path("tests/tmp_test.json")
    data = {"x": 1, "y": "hello"}
    write_json(test_path, data)
    loaded = read_json(test_path)
    assert loaded == data
    test_path.unlink()