from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
