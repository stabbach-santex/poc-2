"""
Base adapter class para transformar datos de diferentes fuentes
al schema canónico de LogiQ AI.
"""

import pandas as pd
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Optional


class DataAdapter(ABC):
    """Clase base para adapters de datos"""
    
    def __init__(self, mapping_file: str):
        """
        Inicializa el adapter con un archivo de mapeo YAML.
        
        Args:
            mapping_file: Ruta al archivo YAML con el mapeo de campos
        """
        self.mapping_file = mapping_file
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict:
        """Carga el archivo de mapeo YAML"""
        with open(self.mapping_file, 'r') as f:
            return yaml.safe_load(f)
    
    def transform(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Transforma un DataFrame según el mapeo configurado.
        
        Args:
            df: DataFrame con datos originales
            table_name: Nombre de la tabla destino (trips, telemetry, alerts, etc.)
        
        Returns:
            DataFrame transformado al schema canónico
        """
        if table_name not in self.mapping:
            raise ValueError(f"Tabla '{table_name}' no encontrada en mapeo")
        
        field_mapping = self.mapping[table_name]
        
        # Crear nuevo DataFrame con campos mapeados
        transformed_data = {}
        for dest_field, source_field in field_mapping.items():
            if source_field in df.columns:
                transformed_data[dest_field] = df[source_field]
            else:
                # Campo no disponible en fuente, llenar con NULL
                transformed_data[dest_field] = None
        
        result_df = pd.DataFrame(transformed_data)
        
        # Normalizar timestamps
        result_df = self._normalize_timestamps(result_df)
        
        return result_df
    
    def _normalize_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza columnas de timestamp a formato ISO8601 UTC.
        """
        timestamp_columns = ['timestamp', 'start_time', 'end_time']
        
        for col in timestamp_columns:
            if col in df.columns:
                try:
                    # Intentar parsear y convertir a ISO8601
                    df[col] = pd.to_datetime(df[col], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                except Exception as e:
                    print(f"⚠️  Warning: No se pudo normalizar columna {col}: {e}")
        
        return df
    
    @abstractmethod
    def load_source_data(self, source_path: str) -> pd.DataFrame:
        """
        Carga datos desde la fuente original.
        Debe ser implementado por cada adapter específico.
        
        Args:
            source_path: Ruta al archivo/API de la fuente
        
        Returns:
            DataFrame con datos originales
        """
        pass
    
    def process(self, source_path: str, table_name: str) -> pd.DataFrame:
        """
        Proceso completo: carga datos, transforma y retorna.
        
        Args:
            source_path: Ruta a los datos originales
            table_name: Tabla destino en schema canónico
        
        Returns:
            DataFrame transformado y listo para insertar
        """
        print(f"📥 Cargando datos desde {source_path}...")
        raw_df = self.load_source_data(source_path)
        
        print(f"🔄 Transformando {len(raw_df)} registros a tabla '{table_name}'...")
        transformed_df = self.transform(raw_df, table_name)
        
        print(f"✅ Transformación completada: {len(transformed_df)} registros")
        return transformed_df


class CSVAdapter(DataAdapter):
    """Adapter para archivos CSV"""
    
    def load_source_data(self, source_path: str) -> pd.DataFrame:
        """Carga datos desde archivo CSV"""
        return pd.read_csv(source_path)


class JSONAdapter(DataAdapter):
    """Adapter para archivos JSON"""
    
    def load_source_data(self, source_path: str) -> pd.DataFrame:
        """Carga datos desde archivo JSON"""
        return pd.read_json(source_path)
