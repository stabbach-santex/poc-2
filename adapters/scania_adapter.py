"""
Adapter para datos de Scania (métricas de vehículos)
"""

from adapters.adapter_base import CSVAdapter


class ScaniaAdapter(CSVAdapter):
    """Adapter específico para datos de Scania"""
    
    def __init__(self):
        super().__init__("mappings/scania_mapping.yaml")
