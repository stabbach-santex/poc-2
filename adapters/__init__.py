"""
Adapters para transformar datos de diferentes fuentes al schema canónico
"""

from adapters.adapter_base import DataAdapter, CSVAdapter, JSONAdapter
from adapters.tera_adapter import TeraAdapter
from adapters.cloudfleet_adapter import CloudfleetAdapter
from adapters.scania_adapter import ScaniaAdapter
from adapters.keeper_adapter import KeeperAdapter

__all__ = [
    'DataAdapter',
    'CSVAdapter',
    'JSONAdapter',
    'TeraAdapter',
    'CloudfleetAdapter',
    'ScaniaAdapter',
    'KeeperAdapter'
]
