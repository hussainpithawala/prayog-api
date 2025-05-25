import xxhash

# Constants should be identical across all instances
BUCKET_HASH_SEED = 42  # Must be the same everywhere
HASH_MAX = 4294967296.0  # 2^32 for 32-bit hashing
FLOAT_TOLERANCE = 1e-6  # For floating point comparisons


class BucketAllocator:
    def __init__(self, buckets):
        """
        Initialize with bucket configuration.

        Args:
            buckets: List of dicts with 'bucket_name' and 'percentage_distribution'
        """
        self._validate_buckets(buckets)
        self.buckets = self._normalize_buckets(buckets)
        self.slots = self._calculate_slots(self.buckets)

    @staticmethod
    def _validate_buckets(buckets):
        """Validate bucket configuration."""
        if not buckets:
            raise ValueError("At least one bucket must be provided")

        total = sum(b['percentage_distribution'] for b in buckets)
        if abs(total - 100.0) > FLOAT_TOLERANCE:
            raise ValueError(f"Bucket percentages must sum to 100 (got {total})")

    @staticmethod
    def _normalize_buckets(buckets):
        """Ensure percentages sum exactly to 100 accounting for floating point."""
        total = sum(b['percentage_distribution'] for b in buckets)
        if abs(total - 100.0) <= FLOAT_TOLERANCE:
            return buckets.copy()

        # Adjust the last bucket to make the total exactly 100
        normalized = buckets.copy()
        normalized[-1] = {
            'bucket_name': normalized[-1]['bucket_name'],
            'percentage_distribution': normalized[-1]['percentage_distribution'] + (100.0 - total)
        }
        return normalized

    @staticmethod
    def _calculate_slots(buckets):
        """Calculate the allocation slots."""
        sorted_buckets = sorted(buckets, key=lambda x: x['bucket_name'])
        slots = []
        threshold = 0.0

        for bucket in sorted_buckets:
            threshold += bucket['percentage_distribution']
            slots.append({
                'name': bucket['bucket_name'],
                'end': threshold
            })

        # Ensure last bucket ends exactly at 100
        if slots:
            slots[-1]['end'] = 100.0

        return slots

    def allocate(self, sample):
        """
        Allocate a sample to a bucket.

        Args:
            sample: Dict with 'experiment_id', 'sampled_entity', and 'sampled_value'

        Returns:
            The allocated bucket name
        """
        key = f"{sample['experiment_id']}:{sample['sampled_entity']}:{sample['sampled_value']}"
        point = (xxhash.xxh32_intdigest(key, seed=BUCKET_HASH_SEED) / HASH_MAX) * 100.0

        # Find the appropriate bucket (using binary search for efficiency)
        low, high = 0, len(self.slots) - 1
        while low <= high:
            mid = (low + high) // 2
            if point <= self.slots[mid]['end'] + FLOAT_TOLERANCE:
                if mid == 0 or point > self.slots[mid - 1]['end'] - FLOAT_TOLERANCE:
                    return self.slots[mid]['name']
                high = mid - 1
            else:
                low = mid + 1

        # Fallback (should theoretically never be reached)
        return self.slots[-1]['name']
