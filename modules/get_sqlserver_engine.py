#%%
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine,text
import urllib

from sqlalchemy.dialects.mssql import NVARCHAR



load_dotenv(verbose=True, override=True)
db_config = {
    'server': os.getenv("SERVER"),
    'database': os.getenv("DATABASE"),
    'username': os.getenv("USERNAME"),
    'password': os.getenv("PASSWORD"),
    'driver': os.getenv("DRIVER")
}

def get_sqlserver_engine():
    """
    Create a SQLAlchemy engine for connecting to a SQL Server database.
    
    Returns:
        sqlalchemy.engine.Engine: The SQLAlchemy engine object.
    """
    # Crear la cadena de conexión ODBC
    odbc_str = f"DRIVER={db_config['driver']};SERVER={db_config['server']};PORT=1433;UID={db_config['username']};DATABASE={db_config['database']};PWD={db_config['password']}"
    connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)

    # Crear el motor de SQLAlchemy
    engine = create_engine(connect_str)
    return engine


# get_sqlserver_engine()

