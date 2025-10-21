"""
Tests para adapters de datos
"""

import pytest
import pandas as pd
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import TeraAdapter, CloudfleetAdapter, ScaniaAdapter, KeeperAdapter


def test_tera_adapter():
    """Test para TeraAdapter"""
    adapter = TeraAdapter()
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'trip_id': ['T001', 'T002'],
        'vehicle_id': ['TRUCK_001', 'TRUCK_002'],
        'driver_code': ['DRV_001', 'DRV_002'],
        'origin_city': ['Buenos Aires', 'Córdoba'],
        'dest_city': ['Rosario', 'Mendoza'],
        'departure_time': ['2025-10-20T08:00:00Z', '2025-10-20T09:00:00Z'],
        'arrival_time': ['2025-10-20T12:00:00Z', '2025-10-20T15:00:00Z'],
        'distance': [300, 450],
        'trip_status': ['finished', 'in_progress']
    })
    
    # Transformar
    result = adapter.transform(test_data, 'trips')
    
    # Verificaciones
    assert 'trip_id' in result.columns
    assert 'truck_id' in result.columns
    assert 'origin' in result.columns
    assert len(result) == 2
    assert result['truck_id'].iloc[0] == 'TRUCK_001'


def test_cloudfleet_adapter():
    """Test para CloudfleetAdapter"""
    adapter = CloudfleetAdapter()
    
    test_data = pd.DataFrame({
        'position_id': ['CF001', 'CF002'],
        'truck_code': ['TRUCK_001', 'TRUCK_002'],
        'recorded_at': ['2025-10-20T08:00:00Z', '2025-10-20T09:00:00Z'],
        'speed_kph': [80, 90],
        'fuel_percentage': [75, 60]
    })
    
    result = adapter.transform(test_data, 'telemetry')
    
    assert 'telemetry_id' in result.columns
    assert 'truck_id' in result.columns
    assert 'speed_kmh' in result.columns
    assert len(result) == 2


def test_scania_adapter():
    """Test para ScaniaAdapter"""
    adapter = ScaniaAdapter()
    
    test_data = pd.DataFrame({
        'metric_id': ['S001', 'S002'],
        'vehicle_vin': ['TRUCK_001', 'TRUCK_002'],
        'timestamp_utc': ['2025-10-20T08:00:00Z', '2025-10-20T09:00:00Z'],
        'velocity_kmh': [85, 95],
        'fuel_level_liters': [120, 100],
        'engine_temperature_celsius': [88, 92]
    })
    
    result = adapter.transform(test_data, 'telemetry')
    
    assert 'engine_temp_c' in result.columns
    assert result['engine_temp_c'].iloc[0] == 88


def test_keeper_adapter():
    """Test para KeeperAdapter"""
    adapter = KeeperAdapter()
    
    test_data = pd.DataFrame({
        'alert_code': ['A001', 'A002'],
        'truck_identifier': ['TRUCK_001', 'TRUCK_002'],
        'event_timestamp': ['2025-10-20T08:00:00Z', '2025-10-20T09:00:00Z'],
        'alert_category': ['temperature', 'speed'],
        'priority_level': ['critical', 'high'],
        'message': ['High temp', 'Speed limit exceeded']
    })
    
    result = adapter.transform(test_data, 'alerts')
    
    assert 'alert_id' in result.columns
    assert 'severity' in result.columns
    assert result['severity'].iloc[0] == 'critical'


def test_adapter_missing_field():
    """Test cuando falta un campo en los datos originales"""
    adapter = CloudfleetAdapter()
    
    # Datos sin fuel_percentage
    test_data = pd.DataFrame({
        'position_id': ['CF001'],
        'truck_code': ['TRUCK_001'],
        'recorded_at': ['2025-10-20T08:00:00Z'],
        'speed_kph': [80]
    })
    
    result = adapter.transform(test_data, 'telemetry')
    
    # Debe tener la columna fuel_level pero con None
    assert 'fuel_level' in result.columns
    assert pd.isna(result['fuel_level'].iloc[0]) or result['fuel_level'].iloc[0] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
