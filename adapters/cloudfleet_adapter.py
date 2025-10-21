"""
Adapter para datos de Cloudfleet (telemetría/posiciones)
"""

from adapters.adapter_base import CSVAdapter


class CloudfleetAdapter(CSVAdapter):
    """Adapter específico para datos de Cloudfleet"""
    
    def __init__(self):
        super().__init__("mappings/cloudfleet_mapping.yaml")
