from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class IQCapture:
    """
    Standardized in-memory complex floating-point signal representation.
    All samples are stored as complex64 array: x[n] = I[n] + j * Q[n].
    """
    samples: np.ndarray  # complex64 array of shape (N,)
    sample_rate: float
    center_freq: Optional[float] = None
    source_format: str = "cf32"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.samples, np.ndarray):
            self.samples = np.asarray(self.samples, dtype=np.complex64)
        elif self.samples.dtype != np.complex64:
            self.samples = self.samples.astype(np.complex64)

    @property
    def num_samples(self) -> int:
        return len(self.samples)

    @property
    def duration_seconds(self) -> float:
        if self.sample_rate and self.sample_rate > 0:
            return float(len(self.samples) / self.sample_rate)
        return 0.0

    @property
    def mean_power(self) -> float:
        if len(self.samples) == 0:
            return 0.0
        return float(np.mean(np.abs(self.samples) ** 2))
