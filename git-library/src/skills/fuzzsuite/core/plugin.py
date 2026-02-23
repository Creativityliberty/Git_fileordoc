from __future__ import annotations
from abc import ABC, abstractmethod
import argparse

class FuzzPlugin(ABC):
    name: str

    @abstractmethod
    def register(self, subparsers: argparse._SubParsersAction) -> None:
        ...
