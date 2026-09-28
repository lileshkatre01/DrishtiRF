from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class IQCapture:
    """
    Standardized in-memory complex floating-point signal object.
    """
    samples: np.ndarray  # complex64 array of shape (N,)
    sample_rate: float
    center_freq: Optional[float] = None
    source_format: str = "cf32"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def num_samples(self) -> int:
        return len(self.samples)

    @property
    def duration_seconds(self) -> float:
        if self.sample_rate and self.sample_rate > 0:
            return len(self.samples) / self.sample_rate
        return 0.0
