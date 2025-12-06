#!/usr/bin/env python3
"""
Main script to choose and load datasets for relationship analysis.
Writes configuration to db_config.json for the notebook to read.
"""

import os
import sys
import json
import getpass
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = 'db_config.json'

# SQLite settings
SQLITE_OLIST_DB = 'olist_ecommerce.db'

# MySQL settings from environment
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')


def save_config(config):
    """Save database configuration for notebook to read."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {CONFIG_FILE}")


def print_header(title):
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)


def get_database_choice():
    print_header("Database Relationship Discovery")
    
    print("\nAvailable databases:\n")
    print("  1. Olist E-Commerce (SQLite - local)")
    print("     9 tables, ~100k orders")
    print("     Clean, well-structured Brazilian e-commerce data\n")
    
    print("  2. TPC-H Benchmark (MySQL - remote)")
    print("     Standard benchmark database without enforced foreign keys")
    print(f"     Host: {MYSQL_HOST}")
    print(f"     Database: {MYSQL_DATABASE}\n")
    
    print("  3. Custom Database")
    print("     Connect to your own MySQL or PostgreSQL database\n")
    
    print("  0. Exit\n")
    
    return input("Select database [1/2/3/0]: ").strip()


def setup_olist():
    """Setup Olist SQLite database."""
    print_header("Setting up Olist Dataset")
    
    if not os.path.exists(SQLITE_OLIST_DB):
        try:
            from setup_database import load_olist_to_sqlite
            load_olist_to_sqlite(SQLITE_OLIST_DB)
        except ImportError:
            print("Error: setup_database.py not found.")
            print("Please ensure the Olist data loader is available.")
            return False
    else:
        print(f"Database already exists: {SQLITE_OLIST_DB}")
    
    config = {
        'database_type': 'sqlite',
        'database_name': 'Olist E-Commerce',
        'sqlite_path': SQLITE_OLIST_DB
    }
    save_config(config)
    
    print_header("Ready")
    print(f"Database: {SQLITE_OLIST_DB}")
    print(f"Size: {os.path.getsize(SQLITE_OLIST_DB) / (1024*1024):.1f} MB")
    print("\nNext: Open and run database_relationship_analysis.ipynb")
    
    return True


def setup_mysql():
    """Verify MySQL connection and save config."""
    print_header("Connecting to TPC-H Database")
    
    try:
        import mysql.connector
        
        print(f"Connecting to {MYSQL_HOST}...")
        
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Connected successfully!\n")
        print(f"Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count:,} rows")
        
        conn.close()
        
        config = {
            'database_type': 'mysql',
            'database_name': 'TPC-H Benchmark',
            'mysql_host': MYSQL_HOST,
            'mysql_port': MYSQL_PORT,
            'mysql_user': MYSQL_USER,
            'mysql_password': MYSQL_PASSWORD,
            'mysql_database': MYSQL_DATABASE
        }
        save_config(config)
        
        print_header("Ready")
        print("Configuration saved.")
        print("\nNext: Open and run database_relationship_analysis.ipynb")
        print("\nNote: Remote database queries may be slow due to network latency.")
        print("The notebook uses optimized queries to minimize this impact.")
        
        return True
        
    except ImportError:
        print("Error: mysql-connector-python not installed")
        print("Run: pip install mysql-connector-python")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def setup_custom():
    """Setup a custom database connection with user-provided credentials."""
    print_header("Custom Database Setup")
    
    print("\nSupported database types:")
    print("  1. MySQL / MariaDB")
    print("  2. PostgreSQL")
    print("  0. Back to main menu\n")
    
    db_choice = input("Select database type [1/2/0]: ").strip()
    
    if db_choice == '0':
        return False
    elif db_choice == '1':
        return setup_custom_mysql()
    elif db_choice == '2':
        return setup_custom_postgres()
    else:
        print("Invalid choice.")
        return False


def setup_custom_mysql():
    """Setup custom MySQL database."""
    print_header("MySQL Connection Details")
    print("(Press Enter to use default values shown in brackets)\n")
    
    host = input("Host [localhost]: ").strip() or 'localhost'
    port_str = input("Port [3306]: ").strip() or '3306'
    user = input("Username [root]: ").strip() or 'root'
    password = getpass.getpass("Password: ")
    database = input("Database name: ").strip()
    
    if not database:
        print("Error: Database name is required.")
        return False
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: Invalid port number '{port_str}'")
        return False
    
    display_name = input(f"Display name [{database}]: ").strip() or database
    
    print(f"\nConnecting to {host}:{port}/{database}...")
    
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Connected successfully!\n")
        print(f"Found {len(tables)} tables:")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count:,} rows")
        
        conn.close()
        
        config = {
            'database_type': 'mysql',
            'database_name': display_name,
            'mysql_host': host,
            'mysql_port': port,
            'mysql_user': user,
            'mysql_password': password,
            'mysql_database': database
        }
        save_config(config)
        
        print_header("Ready")
        print(f"Database: {display_name}")
        print(f"Tables: {len(tables)}")
        print("\nNext: Open and run database_relationship_analysis.ipynb")
        
        return True
        
    except ImportError:
        print("Error: mysql-connector-python not installed")
        print("Run: pip install mysql-connector-python")
        return False
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def setup_custom_postgres():
    """Setup custom PostgreSQL database."""
    print_header("PostgreSQL Connection Details")
    print("(Press Enter to use default values shown in brackets)\n")
    
    host = input("Host [localhost]: ").strip() or 'localhost'
    port_str = input("Port [5432]: ").strip() or '5432'
    user = input("Username [postgres]: ").strip() or 'postgres'
    password = getpass.getpass("Password: ")
    database = input("Database name: ").strip()
    schema = input("Schema [public]: ").strip() or 'public'
    
    if not database:
        print("Error: Database name is required.")
        return False
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: Invalid port number '{port_str}'")
        return False
    
    display_name = input(f"Display name [{database}]: ").strip() or database
    
    print(f"\nConnecting to {host}:{port}/{database}...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (schema,))
        tables = cursor.fetchall()
        
        print(f"Connected successfully!\n")
        print(f"Found {len(tables)} tables in schema '{schema}':")
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table[0]}"')
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count:,} rows")
        
        conn.close()
        
        config = {
            'database_type': 'postgres',
            'database_name': display_name,
            'postgres_host': host,
            'postgres_port': port,
            'postgres_user': user,
            'postgres_password': password,
            'postgres_database': database,
            'postgres_schema': schema
        }
        save_config(config)
        
        print_header("Ready")
        print(f"Database: {display_name}")
        print(f"Schema: {schema}")
        print(f"Tables: {len(tables)}")
        print("\nNext: Open and run database_relationship_analysis.ipynb")
        
        return True
        
    except ImportError:
        print("Error: psycopg2 not installed")
        print("Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def main():
    choice = get_database_choice()
    
    if choice == '0':
        print("Exiting.")
        return
    elif choice == '1':
        setup_olist()
    elif choice == '2':
        setup_mysql()
    elif choice == '3':
        setup_custom()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)