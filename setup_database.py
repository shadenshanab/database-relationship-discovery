import os
import json
import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()

SQLITE_OLIST_DB = os.getenv('SQLITE_OLIST_DB', 'olist_ecommerce.db')
CONFIG_FILE = 'db_config.json'


def load_config():
    """Load database configuration from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Configuration file '{CONFIG_FILE}' not found.\n"
            "Please run main.py first to select a database."
        )
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def connect_database(config=None):
    """
    Establish database connection based on config.
    
    Returns:
        tuple: (connection, is_remote, db_type, config)
    """
    if config is None:
        config = load_config()
    
    db_type = config['database_type']
    
    if db_type == 'sqlite':
        path = config['sqlite_path']
        if not os.path.exists(path):
            raise FileNotFoundError(f"SQLite database not found: {path}")
        conn = sqlite3.connect(path)
        print(f"Connected to SQLite: {path}")
        print(f"File size: {os.path.getsize(path) / (1024*1024):.1f} MB")
        return conn, False, db_type, config
    
    elif db_type == 'mysql':
        import mysql.connector
        conn = mysql.connector.connect(
            host=config['mysql_host'],
            port=config['mysql_port'],
            user=config['mysql_user'],
            password=config['mysql_password'],
            database=config['mysql_database']
        )
        print(f"Connected to MySQL: {config['mysql_host']}/{config['mysql_database']}")
        print("Note: Remote database - using optimized queries to minimize latency")
        return conn, True, db_type, config
    
    elif db_type == 'postgres':
        import psycopg2
        conn = psycopg2.connect(
            host=config['postgres_host'],
            port=config['postgres_port'],
            user=config['postgres_user'],
            password=config['postgres_password'],
            database=config['postgres_database']
        )
        print(f"Connected to PostgreSQL: {config['postgres_host']}/{config['postgres_database']}")
        print(f"Schema: {config.get('postgres_schema', 'public')}")
        print("Note: Remote database - using optimized queries to minimize latency")
        return conn, True, db_type, config
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def get_table_names(conn, db_type, config):
    """Get list of table names from database."""
    if db_type == 'sqlite':
        df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        return df['name'].tolist()
    elif db_type == 'postgres':
        schema = config.get('postgres_schema', 'public')
        df = pd.read_sql(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema}'
        """, conn)
        return df['table_name'].tolist()
    else:  # mysql
        df = pd.read_sql("SHOW TABLES", conn)
        return df.iloc[:, 0].tolist()


def get_column_info(conn, db_type, config, table_name):
    """Get column names and types for a table."""
    if db_type == 'sqlite':
        df = pd.read_sql(f"PRAGMA table_info({table_name})", conn)
        return list(zip(df['name'], df['type']))
    elif db_type == 'postgres':
        schema = config.get('postgres_schema', 'public')
        df = pd.read_sql(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = '{schema}' AND table_name = '{table_name}'
        """, conn)
        return list(zip(df['column_name'], df['data_type']))
    else:  # mysql
        df = pd.read_sql(f"SHOW COLUMNS FROM {table_name}", conn)
        return list(zip(df['Field'], df['Type']))


def quote_identifier(name, db_type, config=None):
    """Quote a table or column name appropriately for the database type."""
    if db_type == 'postgres':
        schema = config.get('postgres_schema', 'public') if config else 'public'
        return f'"{schema}"."{name}"'
    elif db_type == 'mysql':
        return f'`{name}`'
    else:  # sqlite
        return f'"{name}"'


def load_olist_to_sqlite(db_name=None):
    """Load Olist CSV files into SQLite database."""
    if db_name is None:
        db_name = SQLITE_OLIST_DB
    
    conn = sqlite3.connect(db_name)
    
    csv_files = {
        'customers': 'csv_data/olist_customers_dataset.csv',
        'geolocation': 'csv_data/olist_geolocation_dataset.csv',
        'order_items': 'csv_data/olist_order_items_dataset.csv',
        'order_payments': 'csv_data/olist_order_payments_dataset.csv',
        'order_reviews': 'csv_data/olist_order_reviews_dataset.csv',
        'orders': 'csv_data/olist_orders_dataset.csv',
        'products': 'csv_data/olist_products_dataset.csv',
        'sellers': 'csv_data/olist_sellers_dataset.csv',
        'product_category_translation': 'csv_data/product_category_name_translation.csv'
    }
    
    print("Loading Olist E-Commerce dataset to SQLite...")
    print("-" * 60)
    
    for table_name, csv_path in csv_files.items():
        try:
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, index=False, if_exists='replace')
            print(f"[OK] {table_name}: {len(df):,} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"[ERROR] Loading {table_name}: {e}")
    
    _print_summary(conn, db_name)
    conn.close()


def _print_summary(conn, db_name):
    """Print SQLite database summary."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("-" * 60)
    print(f"Database setup complete: {db_name}")
    print(f"  Created {len(tables)} tables:")
    for table in tables:
        print(f"    - {table[0]}")


if __name__ == "__main__":
    print("Running setup_database.py directly...")
    print("Tip: Use main.py to choose between datasets and database types\n")
    load_olist_to_sqlite()