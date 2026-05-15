"""
全局测试配置和fixtures
"""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture
def sample_item_data():
    """提供示例物品数据"""
    return {
        'name': '测试手机',
        'price': 1000.0,
        'purchase_date': '2024-01-01',
        'status': 'active',
        'discontinued_date': None,
        'discontinued_reason': None,
    }


@pytest.fixture
def sample_clothing_data():
    """提供示例衣物数据"""
    return {
        'name': '测试T恤',
        'clothing_type': '上衣',
        'price': 100.0,
        'purchase_date': '2024-01-01',
        'status': 'active',
        'discontinued_date': None,
        'discontinued_reason': None,
    }
