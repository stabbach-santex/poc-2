#!/usr/bin/env python3
"""
Genera datasets simulados para las 4 fuentes de datos:
- Tera (trips)
- Cloudfleet (positions/telemetry)
- Scania (metrics/telemetry)
- Keeper (alerts)
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Configuración
NUM_TRUCKS = 50
NUM_DRIVERS = 60
NUM_TRIPS = 500
NUM_TELEMETRY = 1000
NUM_ALERTS = 300

# Datos base
TRUCK_BRANDS = ["Scania", "Volvo", "Mercedes-Benz", "MAN", "Iveco", "DAF"]
TRUCK_MODELS = ["R450", "FH16", "Actros", "TGX", "S-Way", "XF"]
REGIONS = ["Norte", "Sur", "Este", "Oeste", "Centro"]
CITIES = ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán", 
          "La Plata", "Mar del Plata", "Salta", "Santa Fe", "San Juan"]
ALERT_TYPES = ["temperature", "speed", "fuel", "engine", "brake", "tire_pressure"]
SEVERITIES = ["low", "medium", "high", "critical"]
TRIP_STATUSES = ["finished", "in_progress", "cancelled", "scheduled"]

def generate_timestamp(days_ago_max=30):
    """Genera timestamp aleatorio en los últimos N días"""
    days_ago = random.randint(0, days_ago_max)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    dt = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_tera_trips():
    """Genera datos de viajes (fuente: Tera)"""
    print("📦 Generando tera_trips.csv...")
    
    data = []
    for i in range(NUM_TRIPS):
        trip_id = f"TERA_TRIP_{i+1:04d}"
        truck_id = f"TRUCK_{random.randint(1, NUM_TRUCKS):03d}"
        driver_id = f"DRV_{random.randint(1, NUM_DRIVERS):03d}"
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])
        
        start_time = generate_timestamp(30)
        start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
        duration_hours = random.randint(2, 24)
        end_dt = start_dt + timedelta(hours=duration_hours)
        end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        distance_km = random.randint(100, 1500)
        status = random.choice(TRIP_STATUSES)
        cargo_weight_kg = random.randint(5000, 25000)
        
        data.append({
            "trip_id": trip_id,
            "vehicle_id": truck_id,  # nombre diferente en fuente
            "driver_code": driver_id,  # nombre diferente
            "origin_city": origin,
            "dest_city": destination,
            "departure_time": start_time,
            "arrival_time": end_time,
            "distance": distance_km,
            "trip_status": status,
            "cargo_weight": cargo_weight_kg
        })
    
    df = pd.DataFrame(data)
    df.to_csv("data/tera_trips.csv", index=False)
    print(f"✅ Generados {len(df)} registros en tera_trips.csv")

def generate_cloudfleet_positions():
    """Genera datos de posiciones/telemetría (fuente: Cloudfleet)"""
    print("📡 Generando cloudfleet_positions.csv...")
    
    data = []
    for i in range(NUM_TELEMETRY):
        telemetry_id = f"CF_POS_{i+1:05d}"
        truck_id = f"TRUCK_{random.randint(1, NUM_TRUCKS):03d}"
        timestamp = generate_timestamp(7)  # última semana
        
        speed = random.randint(0, 120)
        fuel_pct = random.randint(10, 100)
        latitude = -34.0 + random.uniform(-5, 5)
        longitude = -64.0 + random.uniform(-5, 5)
        
        data.append({
            "position_id": telemetry_id,
            "truck_code": truck_id,  # nombre diferente
            "recorded_at": timestamp,
            "speed_kph": speed,
            "fuel_percentage": fuel_pct,
            "lat": latitude,
            "lon": longitude
        })
    
    df = pd.DataFrame(data)
    df.to_csv("data/cloudfleet_positions.csv", index=False)
    print(f"✅ Generados {len(df)} registros en cloudfleet_positions.csv")

def generate_scania_metrics():
    """Genera métricas de vehículos (fuente: Scania)"""
    print("🚛 Generando scania_metrics.csv...")
    
    data = []
    for i in range(NUM_TELEMETRY):
        metric_id = f"SCANIA_M_{i+1:05d}"
        truck_id = f"TRUCK_{random.randint(1, NUM_TRUCKS):03d}"
        timestamp = generate_timestamp(7)
        
        engine_temp = random.randint(70, 105)
        fuel_level = random.uniform(10, 100)
        speed = random.randint(0, 120)
        rpm = random.randint(800, 2200)
        odometer = random.randint(50000, 500000)
        
        data.append({
            "metric_id": metric_id,
            "vehicle_vin": truck_id,  # nombre diferente
            "timestamp_utc": timestamp,
            "engine_temperature_celsius": engine_temp,
            "fuel_level_liters": fuel_level,
            "velocity_kmh": speed,
            "engine_rpm": rpm,
            "total_km": odometer
        })
    
    df = pd.DataFrame(data)
    df.to_csv("data/scania_metrics.csv", index=False)
    print(f"✅ Generados {len(df)} registros en scania_metrics.csv")

def generate_keeper_alerts():
    """Genera alertas (fuente: Keeper)"""
    print("🚨 Generando keeper_alerts.csv...")
    
    data = []
    for i in range(NUM_ALERTS):
        alert_id = f"KEEPER_A_{i+1:04d}"
        truck_id = f"TRUCK_{random.randint(1, NUM_TRUCKS):03d}"
        timestamp = generate_timestamp(14)  # últimas 2 semanas
        
        alert_type = random.choice(ALERT_TYPES)
        severity = random.choice(SEVERITIES)
        
        descriptions = {
            "temperature": f"Engine temp {random.randint(95, 110)}°C - sensor {random.randint(1,4)}",
            "speed": f"Speed limit exceeded: {random.randint(120, 150)} km/h",
            "fuel": f"Low fuel level: {random.randint(5, 15)}%",
            "engine": f"Engine fault code: P{random.randint(100, 999)}",
            "brake": f"Brake system warning - pressure low",
            "tire_pressure": f"Tire {random.randint(1,6)} pressure {random.randint(20, 30)} PSI"
        }
        
        description = descriptions.get(alert_type, "Unknown alert")
        
        data.append({
            "alert_code": alert_id,
            "truck_identifier": truck_id,  # nombre diferente
            "event_timestamp": timestamp,
            "alert_category": alert_type,
            "priority_level": severity,
            "message": description,
            "acknowledged": random.choice([True, False])
        })
    
    df = pd.DataFrame(data)
    df.to_csv("data/keeper_alerts.csv", index=False)
    print(f"✅ Generados {len(df)} registros en keeper_alerts.csv")

def generate_master_data():
    """Genera datos maestros de camiones y conductores"""
    print("👥 Generando datos maestros...")
    
    # Trucks
    trucks = []
    for i in range(NUM_TRUCKS):
        truck_id = f"TRUCK_{i+1:03d}"
        plate = f"AB{random.randint(100, 999)}CD"
        brand = random.choice(TRUCK_BRANDS)
        model = random.choice(TRUCK_MODELS)
        driver_id = f"DRV_{random.randint(1, NUM_DRIVERS):03d}"
        region = random.choice(REGIONS)
        status = random.choice(["active", "maintenance", "inactive"])
        
        trucks.append({
            "truck_id": truck_id,
            "plate": plate,
            "model": model,
            "brand": brand,
            "driver_id": driver_id,
            "region": region,
            "status": status
        })
    
    df_trucks = pd.DataFrame(trucks)
    df_trucks.to_csv("data/master_trucks.csv", index=False)
    print(f"✅ Generados {len(df_trucks)} camiones en master_trucks.csv")
    
    # Drivers
    drivers = []
    first_names = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Diego", "Sofia", 
                   "Miguel", "Valentina", "Jorge", "Camila", "Roberto", "Lucía", "Fernando"]
    last_names = ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", 
                  "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández"]
    
    for i in range(NUM_DRIVERS):
        driver_id = f"DRV_{i+1:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        license = f"LIC{random.randint(100000, 999999)}"
        
        drivers.append({
            "driver_id": driver_id,
            "name": name,
            "license": license
        })
    
    df_drivers = pd.DataFrame(drivers)
    df_drivers.to_csv("data/master_drivers.csv", index=False)
    print(f"✅ Generados {len(df_drivers)} conductores en master_drivers.csv")

def main():
    print("=" * 50)
    print("🎲 Generador de Datos Simulados - LogiQ AI")
    print("=" * 50)
    print()
    
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Generar todos los datasets
    generate_master_data()
    generate_tera_trips()
    generate_cloudfleet_positions()
    generate_scania_metrics()
    generate_keeper_alerts()
    
    print()
    print("=" * 50)
    print("✅ Generación de datos completada!")
    print("=" * 50)
    print()
    print("Archivos generados en data/:")
    print("  - master_trucks.csv")
    print("  - master_drivers.csv")
    print("  - tera_trips.csv")
    print("  - cloudfleet_positions.csv")
    print("  - scania_metrics.csv")
    print("  - keeper_alerts.csv")
    print()

if __name__ == "__main__":
    main()
