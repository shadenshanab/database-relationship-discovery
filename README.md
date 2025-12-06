# Database Relationship Discovery

A toolkit for identifying foreign key relationships in databases that don't have enforced constraints. This is common in production systems where FK constraints are skipped for performance reasons, or in legacy databases that were migrated without schema documentation.

## What This Does

The analysis identifies potential FK relationships using multiple signals:

- Column naming patterns (like `customer_id` suggesting a link to a `customers` table)
- Data type compatibility between columns
- Value overlap analysis (what percentage of FK values exist in the referenced table)
- Cardinality profiling (determining 1:1, 1:M, or M:M relationships)

Each discovered relationship gets a confidence score based on how strongly these signals align.

## Quick Start

The notebook has already been executed against the TPC-H benchmark database, so you can review the outputs without running anything. Just open `database_relationship_analysis.ipynb` and scroll through the results.

If you want to run the analysis yourself, follow the steps below.

## Running the Analysis

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas sqlalchemy mysql-connector-python python-dotenv jupyter
```

Optional (for extra features):

```bash
pip install scikit-learn ydata-profiling
pip install psycopg2-binary  # for PostgreSQL support
```

### 3. Choose a Database

Run the main script to select which database to analyze:
```bash
python main.py
```

You'll see three options:

1. **Olist E-Commerce (SQLite)** - A local dataset included in this repo. Good for testing.
2. **TPC-H (MySQL)** - A remote benchmark database. This is what the notebook outputs currently show.
3. **Custom Database** - Connect to your own MySQL or PostgreSQL database.

The script will save your choice to `db_config.json`, which the notebook reads automatically.

### Using Your Own Database

Select option 3 and follow the prompts:

```
$ python main.py

------------------------------------------------------------
Database Relationship Discovery
------------------------------------------------------------

Available databases:

  1. Olist E-Commerce (SQLite - local)
  2. TPC-H Benchmark (MySQL - remote)
  3. Custom Database

Select database [1/2/3/0]: 3

------------------------------------------------------------
Custom Database Setup
------------------------------------------------------------

Supported database types:
  1. MySQL / MariaDB
  2. PostgreSQL

Select database type [1/2/0]: 1

------------------------------------------------------------
MySQL Connection Details
------------------------------------------------------------

Host [localhost]: db.example.com
Port [3306]: 
Username [root]: myuser
Password: 
Database name: production_db
Display name [production_db]: Production Analytics

Connecting to db.example.com:3306/production_db...
Connected successfully!

Found 12 tables:
  users: 50,000 rows
  orders: 1,200,000 rows
  ...
```

The script tests the connection before saving, so you'll know immediately if there's an issue.

### 4. Run the Notebook
```bash
jupyter notebook database_relationship_analysis.ipynb
```

Then run all cells. The notebook will connect to whichever database you selected in step 2.

## Included Files
```
├── main.py                              # Database selector script
├── setup_database.py                    # Connection utilities
├── database_relationship_analysis.ipynb # Main analysis notebook
├── db_config.json                       # Generated config (created by main.py)
├── data/
│   └── olist/                           # Olist CSV files for local testing
├── profiles/                            # Pre-generated data profiles
└── README.md
```

## Testing with the Olist Dataset

The Olist e-commerce dataset is included so you can test the analysis locally without needing database credentials. Run `main.py`, select option 1, and the script will load the CSVs into a local SQLite database.

The notebook outputs you see were generated against TPC-H (a standard benchmark database), but the Olist dataset works the same way and has similar relationship patterns.

## What the Notebook Covers

1. **Schema Discovery** - Catalogs all tables, columns, and data types
2. **FK Detection** - Identifies columns that look like foreign keys based on naming
3. **Candidate Generation** - Matches FK columns to potential primary keys in other tables
4. **Statistical Validation** - Tests each candidate by checking actual value overlap
5. **Results Classification** - Groups relationships by confidence level
6. **Data Quality Analysis** - Identifies orphaned records and NULL values
7. **Data Profiling** - Optional HTML reports for each table (requires ydata-profiling)
8. **Exhaustive Analysis** - Checks for FKs that don't follow naming conventions
9. **ML Exploration** - Demonstrates how machine learning could improve detection

## Output

The notebook exports results to `discovered_relationships_{database_type}.csv` with columns:

- `relationship` - The proposed FK relationship (e.g., `orders.customer_id → customers.id`)
- `confidence` - Score from 0-100 indicating likelihood
- `inclusion_pct` - Percentage of FK values that exist in the referenced table
- `cardinality` - Relationship type (1:1, 1:M, M:M)
- `detection_basis` - Which signals contributed to the match

## Notes

- Remote database queries can be slow due to network latency. The notebook uses optimized queries that fetch distinct values once per column, then does comparisons locally.
- The ML section uses pseudo-labels (the confidence scores) since we don't have ground truth. In production, you'd train on databases with known FK constraints.
- Some relationships appear twice in opposite directions (e.g., `orders.customer_id → customers.id` and `customers.id → orders.customer_id`). The first direction is the actual FK; the reverse just indicates the values match.
- PostgreSQL connections respect the schema setting—if your tables are in a non-public schema, specify it during setup.

## Requirements

- Python 3.7+
- pandas
- mysql-connector-python (for MySQL)
- python-dotenv
- jupyter

Optional:
- psycopg2-binary (for PostgreSQL)
- scikit-learn (for ML section)
- ydata-profiling (for data profiling reports)
