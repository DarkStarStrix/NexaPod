import pytest


class DummyConfig:
    def __init__(self):
        self.config = {
            'coordinator_url': 'http://localhost:8000',
            'private_key_path': '/tmp/client_ed25519.key',
            'node_id': 'testnode',
            'poll_interval': 1
        }

    def __getitem__(self, k):
        return self.config[k]

    def get(self, k, default=None):
        return self.config.get(k, default)


def test_dummy_config_get():
    config = DummyConfig()
    assert config['node_id'] == 'testnode'
    assert config.get('poll_interval') == 1
    assert config.get('missing', 'default') == 'default'


def test_basic_math():
    assert 1 + 1 == 2


def test_string_ops():
    s = "nexapod"
    assert s.upper() == "NEXAPOD"
    assert s[::-1] == "dopaxen"


def test_list_ops():
    data = [1, 2, 3]
    assert len(data) == 3
    assert data[0] == 1


def test_dict_ops():
    d = {"a": 1, "b": 2}
    assert d["a"] == 1
    assert "b" in d
    
