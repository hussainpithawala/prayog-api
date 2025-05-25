import pytest
from unittest.mock import patch
from app.services.bucket_allocator import BucketAllocator
import xxhash


@pytest.fixture
def valid_buckets():
    return [
        {'bucket_name': 'control', 'percentage_distribution': 30},
        {'bucket_name': 'variant1', 'percentage_distribution': 50},
        {'bucket_name': 'variant2', 'percentage_distribution': 20}
    ]


@pytest.fixture
def sample_data():
    return {
        'experiment_id': 'exp1',
        'sampled_entity': 'user123',
        'sampled_value': 'valueX'
    }


@pytest.fixture
def allocator(valid_buckets):
    return BucketAllocator(valid_buckets)


def test_initialization(valid_buckets):
    """Test initialization with valid bucket configuration"""
    allocator = BucketAllocator(valid_buckets)
    assert len(allocator.slots) == 3
    assert allocator.slots[-1]['end'] == pytest.approx(100.0)


@pytest.mark.parametrize("buckets, expected_error", [
    ([], ValueError),  # Empty buckets
    ([{'bucket_name': 'A', 'percentage_distribution': 30},
      {'bucket_name': 'B', 'percentage_distribution': 60}], ValueError),  # Sums to 90
    ([{'bucket_name': 'A', 'percentage_distribution': -10},
      {'bucket_name': 'B', 'percentage_distribution': 120}], ValueError)  # Invalid percentages
])
def test_invalid_bucket_configurations(buckets, expected_error):
    """Test initialization with invalid bucket configurations"""
    with pytest.raises(expected_error):
        BucketAllocator(buckets)


def test_bucket_normalization():
    """Test that buckets are normalized to sum exactly to 100"""
    slightly_off_buckets = [
        {'bucket_name': 'A', 'percentage_distribution': 33.333333},
        {'bucket_name': 'B', 'percentage_distribution': 33.333333},
        {'bucket_name': 'C', 'percentage_distribution': 33.333333}  # Sums to 99.999
    ]
    allocator = BucketAllocator(slightly_off_buckets)
    total = sum(b['percentage_distribution'] for b in allocator.buckets)
    assert total == pytest.approx(100.0)
    assert allocator.buckets[-1]['bucket_name'] == 'C'


def test_consistent_allocation(allocator, sample_data):
    """Test that same input always gets same bucket"""
    result1 = allocator.allocate(sample_data)
    result2 = allocator.allocate(sample_data)
    assert result1 == result2


def test_deterministic_across_instances(valid_buckets, sample_data):
    """Test that different instances produce same results"""
    allocator1 = BucketAllocator(valid_buckets)
    allocator2 = BucketAllocator(valid_buckets)
    assert allocator1.allocate(sample_data) == allocator2.allocate(sample_data)


@pytest.mark.parametrize("hash_value, expected_bucket", [
    (0, 'control'),  # Minimum hash value
    (4294967295, 'variant2'),  # Maximum hash value (2^32 - 1)
    (2147483648, 'variant1')  # Midpoint hash value
])
def test_edge_case_allocations(allocator, sample_data, hash_value, expected_bucket):
    """Test allocation at specific hash values"""
    with patch('xxhash.xxh32_intdigest', return_value=hash_value):
        assert allocator.allocate(sample_data) == expected_bucket


def test_single_bucket_case():
    """Test with single bucket configuration"""
    allocator = BucketAllocator([{'bucket_name': 'only', 'percentage_distribution': 100}])
    sample = {'experiment_id': 'x', 'sampled_entity': 'y', 'sampled_value': 'z'}
    assert allocator.allocate(sample) == 'only'


def test_slots_calculation():
    """Test slots are calculated correctly and sorted by name"""
    buckets = [
        {'bucket_name': 'B', 'percentage_distribution': 20},
        {'bucket_name': 'A', 'percentage_distribution': 30},
        {'bucket_name': 'C', 'percentage_distribution': 50}
    ]
    allocator = BucketAllocator(buckets)

    assert [s['name'] for s in allocator.slots] == ['A', 'B', 'C']
    assert allocator.slots[0]['end'] == pytest.approx(30.0)
    assert allocator.slots[1]['end'] == pytest.approx(50.0)  # 30 + 20
    assert allocator.slots[2]['end'] == pytest.approx(100.0)


def test_bucket_distribution():
    """Test that allocation roughly matches percentage distribution"""
    buckets = [
        {'bucket_name': 'A', 'percentage_distribution': 70},
        {'bucket_name': 'B', 'percentage_distribution': 30}
    ]
    allocator = BucketAllocator(buckets)

    # Use fixed samples to test distribution
    samples = [{'experiment_id': f'exp{i}', 'sampled_entity': f'user{i}', 'sampled_value': 'test'}
               for i in range(1000)]

    counts = {'A': 0, 'B': 0}
    for sample in samples:
        bucket = allocator.allocate(sample)
        counts[bucket] += 1

    # Allow ±3% tolerance
    assert counts['A'] == pytest.approx(700, abs=30)
    assert counts['B'] == pytest.approx(300, abs=30)


@pytest.mark.parametrize("invalid_sample", [
    {'wrong_key': 'value'},  # Missing required fields
    {},  # Empty sample
    {'experiment_id': 'x'},  # Missing other fields
    {'experiment_id': 'x', 'sampled_entity': 'y'}  # Missing sampled_value
])
def test_invalid_sample_data(allocator, invalid_sample):
    """Test handling of invalid sample data"""
    with pytest.raises(KeyError):
        allocator.allocate(invalid_sample)
