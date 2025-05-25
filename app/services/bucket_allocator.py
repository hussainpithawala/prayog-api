import xxhash
from typing import Dict, List
from functools import lru_cache
import threading

BUCKET_HASH_SEED = 42  # Must be identical across all instances
HASH_MAX = 4294967296.0  # 2^32 for 32-bit hashing
FLOAT_TOLERANCE = 1e-6


class BucketAllocator:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BucketAllocator, cls).__new__(cls)
                cls._instance._experiments: Dict[str, List[Dict]] = {}
                cls._instance._locks: Dict[str, threading.Lock] = {}
        return cls._instance

    def configure_experiment(self, experiment_id: str, buckets: List[Dict]):
        """Configure buckets for an experiment in a thread-safe way"""
        if experiment_id not in self._locks:
            with self._lock:
                if experiment_id not in self._locks:
                    self._locks[experiment_id] = threading.Lock()

        with self._locks[experiment_id]:
            self._validate_buckets(buckets)
            self._experiments[experiment_id] = self._normalize_buckets(buckets)

    @staticmethod
    def _validate_buckets(buckets: List[Dict]):
        """Validate bucket configuration"""
        if not buckets:
            raise ValueError("At least one bucket must be provided")

        total = sum(b['percentage_distribution'] for b in buckets)
        if abs(total - 100.0) > FLOAT_TOLERANCE:
            raise ValueError(f"Bucket percentages must sum to 100 (got {total})")

    @staticmethod
    def _normalize_buckets(buckets: List[Dict]) -> List[Dict]:
        """Ensure percentages sum exactly to 100 accounting for floating point"""
        total = sum(b['percentage_distribution'] for b in buckets)
        if abs(total - 100.0) <= FLOAT_TOLERANCE:
            return buckets.copy()

        normalized = buckets.copy()
        normalized[-1]['percentage_distribution'] += (100.0 - total)
        return normalized

    @lru_cache(maxsize=1024)
    def _get_slots(self, experiment_id: str) -> List[Dict]:
        """Calculate slots for an experiment with caching"""
        buckets = sorted(
            self._experiments[experiment_id],
            key=lambda x: x['bucket_name']
        )
        slots = []
        threshold = 0.0

        for bucket in buckets:
            threshold += bucket['percentage_distribution']
            slots.append({
                'name': bucket['bucket_name'],
                'end': threshold
            })

        if slots:
            slots[-1]['end'] = 100.0

        return slots

    def allocate(self, experiment_id: str, sample: Dict) -> str:
        """
        Allocate a sample to a bucket in the specified experiment

        Args:
            experiment_id: ID of the experiment to allocate within
            sample: Dict containing 'entity_id' and optionally other fields

        Returns:
            The allocated bucket name
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not configured")

        slots = self._get_slots(experiment_id)
        key = f"{experiment_id}:{sample['entity_id']}"
        point = (xxhash.xxh32_intdigest(key, seed=BUCKET_HASH_SEED) / HASH_MAX) * 100.0

        # Binary search for efficient allocation
        low, high = 0, len(slots) - 1
        while low <= high:
            mid = (low + high) // 2
            if point <= slots[mid]['end'] + FLOAT_TOLERANCE:
                if mid == 0 or point > slots[mid - 1]['end'] - FLOAT_TOLERANCE:
                    return slots[mid]['name']
                high = mid - 1
            else:
                low = mid + 1

        return slots[-1]['name']