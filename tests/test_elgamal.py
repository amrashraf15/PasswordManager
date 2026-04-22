import json

import pytest

import crypto.elgamal as elgamal


@pytest.fixture
def temp_params_file(tmp_path, monkeypatch):
    """
    Redirect ELGAMAL_PARAMS_FILE to a temporary JSON file
    so tests do not use the real shared params file.
    """
    params_file = tmp_path / "elgamal_params.json"
    monkeypatch.setattr(elgamal, "ELGAMAL_PARAMS_FILE", params_file) # replace real file path with temp file path
    return params_file


def write_params(path, p, alpha):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"p": p, "alpha": alpha}, f, indent=2)


def test_validate_elgamal_params_accepts_valid_values():
    # 23 is prime, 5 is a primitive root mod 23
    elgamal.validate_elgamal_params(23, 5)


def test_validate_elgamal_params_rejects_non_prime_p():
    with pytest.raises(ValueError, match="prime"):
        elgamal.validate_elgamal_params(21, 5)


def test_validate_elgamal_params_rejects_non_primitive_root():
    # for p=23, alpha=4 is not a primitive root
    with pytest.raises(ValueError, match="primitive root"):
        elgamal.validate_elgamal_params(23, 4)


def test_load_elgamal_params_reads_valid_file(temp_params_file):
    write_params(temp_params_file, 23, 5)

    params = elgamal.load_elgamal_params()

    assert params == {
        "p": 23,
        "alpha": 5,
    }


def test_load_elgamal_params_raises_when_keys_missing(temp_params_file):
    with open(temp_params_file, "w", encoding="utf-8") as f:
        json.dump({"p": 23}, f)

    with pytest.raises(ValueError, match="contain 'p' and 'alpha'"):
        elgamal.load_elgamal_params()


def test_generate_private_key_in_valid_range():
    p = 23
    x = elgamal.generate_private_key(p)

    assert 2 <= x <= p - 2


def test_generate_public_key_matches_modular_exponentiation():
    p = 23
    alpha = 5
    private_key = 6

    y = elgamal.generate_public_key(p, alpha, private_key)

    assert y == pow(alpha, private_key, p)


def test_generate_keypair_returns_expected_fields(temp_params_file):
    write_params(temp_params_file, 23, 5)

    private_key_data, public_key_data = elgamal.generate_keypair()

    assert "p" in private_key_data
    assert "alpha" in private_key_data
    assert "x" in private_key_data

    assert "p" in public_key_data
    assert "alpha" in public_key_data
    assert "y" in public_key_data

    assert private_key_data["p"] == 23
    assert private_key_data["alpha"] == 5
    assert public_key_data["p"] == 23
    assert public_key_data["alpha"] == 5


def test_generate_keypair_public_matches_private(temp_params_file):
    write_params(temp_params_file, 23, 5)

    private_key_data, public_key_data = elgamal.generate_keypair()

    p = private_key_data["p"]
    alpha = private_key_data["alpha"]
    x = private_key_data["x"]
    y = public_key_data["y"]

    assert y == pow(alpha, x, p)


def test_save_and_load_private_key(tmp_path):
    private_key_path = tmp_path / "private_key.json"
    private_key_data = {
        "p": 23,
        "alpha": 5,
        "x": 7,
    }

    elgamal.save_private_key(private_key_path, private_key_data)
    loaded = elgamal.load_private_key(private_key_path)

    assert loaded == private_key_data


def test_save_and_load_public_key(tmp_path):
    public_key_path = tmp_path / "public_key.json"
    public_key_data = {
        "p": 23,
        "alpha": 5,
        "y": 17,
    }

    elgamal.save_public_key(public_key_path, public_key_data)
    loaded = elgamal.load_public_key(public_key_path)

    assert loaded == public_key_data


def test_load_private_key_raises_for_missing_fields(tmp_path):
    private_key_path = tmp_path / "private_key.json"

    with open(private_key_path, "w", encoding="utf-8") as f:
        json.dump({"p": 23, "alpha": 5}, f)

    with pytest.raises(ValueError, match="Private key must contain"):
        elgamal.load_private_key(private_key_path)


def test_load_public_key_raises_for_missing_fields(tmp_path):
    public_key_path = tmp_path / "public_key.json"

    with open(public_key_path, "w", encoding="utf-8") as f:
        json.dump({"p": 23, "alpha": 5}, f)

    with pytest.raises(ValueError, match="Public key must contain"):
        elgamal.load_public_key(public_key_path)


def test_initialize_user_keys_creates_both_files(temp_params_file, tmp_path):
    write_params(temp_params_file, 23, 5)

    private_key_path = tmp_path / "private_key.json"
    public_key_path = tmp_path / "public_key.json"

    elgamal.initialize_user_keys(private_key_path, public_key_path)

    assert private_key_path.exists()
    assert public_key_path.exists()

    private_data = elgamal.load_private_key(private_key_path)
    public_data = elgamal.load_public_key(public_key_path)

    assert private_data["p"] == 23
    assert private_data["alpha"] == 5
    assert public_data["p"] == 23
    assert public_data["alpha"] == 5
    assert public_data["y"] == pow(
        private_data["alpha"],
        private_data["x"],
        private_data["p"],
    )


def test_initialize_user_keys_does_not_overwrite_existing_files(temp_params_file, tmp_path):
    write_params(temp_params_file, 23, 5)

    private_key_path = tmp_path / "private_key.json"
    public_key_path = tmp_path / "public_key.json"

    original_private = {
        "p": 23,
        "alpha": 5,
        "x": 9,
    }
    original_public = {
        "p": 23,
        "alpha": 5,
        "y": pow(5, 9, 23),
    }

    with open(private_key_path, "w", encoding="utf-8") as f:
        json.dump(original_private, f, indent=2)

    with open(public_key_path, "w", encoding="utf-8") as f:
        json.dump(original_public, f, indent=2)

    elgamal.initialize_user_keys(private_key_path, public_key_path)

    loaded_private = elgamal.load_private_key(private_key_path)
    loaded_public = elgamal.load_public_key(public_key_path)

    assert loaded_private == original_private
    assert loaded_public == original_public