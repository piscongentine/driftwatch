"""Feast entity: one physical machine, found by machine_id.

Reads : nothing.
Writes: nothing (Feast registers it when the store is applied).
"""
from feast import Entity
from feast.value_type import ValueType

machine = Entity(
    name="machine",
    join_keys=["machine_id"],
    value_type=ValueType.INT64,
    description="A machine on the shop floor",
)
