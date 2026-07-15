from __future__ import annotations

from abc import ABC, abstractmethod

from ayx_growth_intel.config import SourceConfig
from ayx_growth_intel.models import CollectionBatch


class Collector(ABC):
    @abstractmethod
    def collect(self, source: SourceConfig) -> CollectionBatch:
        raise NotImplementedError
