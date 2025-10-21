"""
Adapter para datos de Tera (viajes)
"""

from adapters.adapter_base import CSVAdapter


class TeraAdapter(CSVAdapter):
    """Adapter específico para datos de Tera"""
    
    def __init__(self):
        super().__init__("mappings/tera_mapping.yaml")
