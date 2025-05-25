import pytest
from unittest.mock import patch
from app.services.bucket_allocator import BucketAllocator
import threading
import xxhash


@pytest.fixture
def allocator():
    # Clear singleton instance for each test
    BucketAllocator._instance = None
    return BucketAllocator()


@pytest.fixture
def experiment_config():
    return [
        {'bucket_name': 'control', 'percentage_distribution': 30},
        {'bucket_name': 'variant1', 'percentage_distribution': 50},
        {'bucket_name': 'variant2', 'percentage_distribution': 20}
    ]


@pytest.fixture
def sample_data():
    return {'entity_id': 'user123'}


def test_singleton_pattern(allocator):
    """Test that only one instance exists"""
    allocator2 = BucketAllocator()
    assert allocator is allocator2


def test_configure_experiment(allocator, experiment_config):
    """Test experiment configuration"""
    allocator.configure_experiment('exp1', experiment_config)
    assert 'exp1' in allocator._experiments


def test_invalid_bucket_configuration(allocator):
    """Test invalid bucket configurations"""
    with pytest.raises(ValueError):
        allocator.configure_experiment('exp1', [])

    with pytest.raises(ValueError):
        allocator.configure_experiment('exp2', [
            {'bucket_name': 'A', 'percentage_distribution': 50},
            {'bucket_name': 'B', 'percentage_distribution': 40}
        ])


def test_allocation_consistency(allocator, experiment_config, sample_data):
    """Test consistent allocation for same input"""
    allocator.configure_experiment('exp1', experiment_config)
    result1 = allocator.allocate('exp1', sample_data)
    result2 = allocator.allocate('exp1', sample_data)
    assert result1 == result2


@pytest.mark.parametrize("hash_value, expected_bucket", [
    (0, 'control'),  # Minimum hash
    (2147483648, 'variant1'),  # Midpoint
    (4294967295, 'variant2')  # Maximum hash
])
def test_edge_case_allocations(allocator, experiment_config, sample_data, hash_value, expected_bucket):
    """Test allocation at specific hash values"""
    allocator.configure_experiment('exp1', experiment_config)
    with patch('xxhash.xxh32_intdigest', return_value=hash_value):
        assert allocator.allocate('exp1', sample_data) == expected_bucket


def test_thread_safety(allocator, experiment_config):
    """Test thread-safe initialization and configuration"""
    results = []

    def configure_and_allocate():
        a = BucketAllocator()
        a.configure_experiment('exp1', experiment_config)
        results.append(a.allocate('exp1', {'entity_id': 'user123'}))

    threads = [threading.Thread(target=configure_and_allocate) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All allocations should be identical
    assert len(set(results)) == 1


def test_multiple_experiments(allocator):
    """Test handling of multiple experiments"""
    allocator.configure_experiment('exp1', [
        {'bucket_name': 'A', 'percentage_distribution': 50},
        {'bucket_name': 'B', 'percentage_distribution': 50}
    ])

    allocator.configure_experiment('exp2', [
        {'bucket_name': 'X', 'percentage_distribution': 70},
        {'bucket_name': 'Y', 'percentage_distribution': 30}
    ])

    assert allocator.allocate('exp1', {'entity_id': 'user1'}) in ('A', 'B')
    assert allocator.allocate('exp2', {'entity_id': 'user1'}) in ('X', 'Y')


def test_slots_caching(allocator, experiment_config):
    """Test that slots are properly cached"""
    allocator.configure_experiment('exp1', experiment_config)
    slots1 = allocator._get_slots('exp1')
    slots2 = allocator._get_slots('exp1')
    assert slots1 is slots2  # Same object from cache


def test_distribution_accuracy(allocator):
    """Test that allocation follows percentage distribution"""
    allocator.configure_experiment('exp1', [
        {'bucket_name': 'A', 'percentage_distribution': 70},
        {'bucket_name': 'B', 'percentage_distribution': 30}
    ])

    counts = {'A': 0, 'B': 0}
    for i in range(1000):
        bucket = allocator.allocate('exp1', {'entity_id': f'user{i}'})
        counts[bucket] += 1

    assert counts['A'] == pytest.approx(700, abs=30)
    assert counts['B'] == pytest.approx(300, abs=30)


def test_unconfigured_experiment(allocator, sample_data):
    """Test handling of unconfigured experiments"""
    with pytest.raises(ValueError):
        allocator.allocate('unknown_exp', sample_data)