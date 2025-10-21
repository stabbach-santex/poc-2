"""
Adapter para datos de Keeper (alertas)
"""

from adapters.adapter_base import CSVAdapter


class KeeperAdapter(CSVAdapter):
    """Adapter específico para datos de Keeper"""
    
    def __init__(self):
        super().__init__("mappings/keeper_mapping.yaml")
