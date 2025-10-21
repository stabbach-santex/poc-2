#!/usr/bin/env python3
"""
Carga datos desde CSVs usando adapters y los inserta en SQLite.
"""

import sqlite3
import pandas as pd
import os
import sys

# Agregar directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import TeraAdapter, CloudfleetAdapter, ScaniaAdapter, KeeperAdapter


DB_PATH = "data/logiq.db"


def create_schema(conn):
    """Crea el schema canónico en SQLite"""
    print("🏗️  Creando schema canónico...")
    
    cursor = conn.cursor()
    
    # Tabla: trucks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trucks (
            truck_id TEXT PRIMARY KEY,
            plate TEXT,
            model TEXT,
            brand TEXT,
            driver_id TEXT,
            region TEXT,
            status TEXT
        )
    """)
    
    # Tabla: drivers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id TEXT PRIMARY KEY,
            name TEXT,
            license TEXT
        )
    """)
    
    # Tabla: trips
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id TEXT PRIMARY KEY,
            truck_id TEXT,
            origin TEXT,
            destination TEXT,
            start_time TEXT,
            end_time TEXT,
            distance_km REAL,
            status TEXT,
            FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
        )
    """)
    
    # Tabla: telemetry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            telemetry_id TEXT PRIMARY KEY,
            truck_id TEXT,
            timestamp TEXT,
            speed_kmh REAL,
            fuel_level REAL,
            engine_temp_c REAL,
            FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
        )
    """)
    
    # Tabla: alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            truck_id TEXT,
            timestamp TEXT,
            alert_type TEXT,
            severity TEXT,
            description TEXT,
            FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
        )
    """)
    
    conn.commit()
    print("✅ Schema creado exitosamente")


def load_master_data(conn):
    """Carga datos maestros (trucks y drivers)"""
    print("\n📊 Cargando datos maestros...")
    
    # Cargar trucks
    if os.path.exists("data/master_trucks.csv"):
        df_trucks = pd.read_csv("data/master_trucks.csv")
        df_trucks.to_sql("trucks", conn, if_exists="replace", index=False)
        print(f"✅ Cargados {len(df_trucks)} camiones")
    
    # Cargar drivers
    if os.path.exists("data/master_drivers.csv"):
        df_drivers = pd.read_csv("data/master_drivers.csv")
        df_drivers.to_sql("drivers", conn, if_exists="replace", index=False)
        print(f"✅ Cargados {len(df_drivers)} conductores")


def load_tera_data(conn):
    """Carga datos de Tera (trips)"""
    print("\n📦 Procesando datos de Tera...")
    
    adapter = TeraAdapter()
    df = adapter.process("data/tera_trips.csv", "trips")
    
    # Insertar en SQLite
    df.to_sql("trips", conn, if_exists="replace", index=False)
    print(f"✅ Insertados {len(df)} viajes")


def load_cloudfleet_data(conn):
    """Carga datos de Cloudfleet (telemetry)"""
    print("\n📡 Procesando datos de Cloudfleet...")
    
    adapter = CloudfleetAdapter()
    df = adapter.process("data/cloudfleet_positions.csv", "telemetry")
    
    # Insertar en SQLite (append para no sobrescribir datos de Scania)
    df.to_sql("telemetry", conn, if_exists="append", index=False)
    print(f"✅ Insertados {len(df)} registros de telemetría")


def load_scania_data(conn):
    """Carga datos de Scania (telemetry)"""
    print("\n🚛 Procesando datos de Scania...")
    
    adapter = ScaniaAdapter()
    df = adapter.process("data/scania_metrics.csv", "telemetry")
    
    # Insertar en SQLite (append)
    df.to_sql("telemetry", conn, if_exists="append", index=False)
    print(f"✅ Insertados {len(df)} registros de telemetría")


def load_keeper_data(conn):
    """Carga datos de Keeper (alerts)"""
    print("\n🚨 Procesando datos de Keeper...")
    
    adapter = KeeperAdapter()
    df = adapter.process("data/keeper_alerts.csv", "alerts")
    
    # Insertar en SQLite
    df.to_sql("alerts", conn, if_exists="replace", index=False)
    print(f"✅ Insertados {len(df)} alertas")


def show_summary(conn):
    """Muestra resumen de datos cargados"""
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE DATOS CARGADOS")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    tables = ["trucks", "drivers", "trips", "telemetry", "alerts"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:15s}: {count:5d} registros")
    
    print("=" * 50)


def main():
    print("=" * 50)
    print("🔄 Carga de Datos - LogiQ AI")
    print("=" * 50)
    
    # Conectar a SQLite
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Crear schema
        create_schema(conn)
        
        # Cargar datos maestros
        load_master_data(conn)
        
        # Cargar datos de fuentes usando adapters
        load_tera_data(conn)
        load_cloudfleet_data(conn)
        load_scania_data(conn)
        load_keeper_data(conn)
        
        # Mostrar resumen
        show_summary(conn)
        
        print("\n✅ Carga de datos completada exitosamente!")
        print(f"📁 Base de datos: {DB_PATH}")
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()
