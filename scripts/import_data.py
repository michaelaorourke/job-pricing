#!/usr/bin/env python3
"""
Import Mercer and Lattice CSV data into PostgreSQL HRAnalyticsDB
"""

import sys
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import uuid

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Database connection
DATABASE_URL = "postgresql://admin:password@localhost:5432/hranalyticsdb"

def connect_db():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def import_mercer_data(filepath):
    """Import Mercer benchmark data"""
    print(f"Importing Mercer data from {filepath}...")

    df = pd.read_csv(filepath)
    conn = connect_db()
    cursor = conn.cursor()

    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        record = (
            str(uuid.uuid4()),  # id
            'mercer',  # source_type
            os.path.basename(filepath),  # source_file
            row.get('job_family'),
            row.get('job_code'),
            None,  # job_title (not in mercer data)
            int(row.get('level')) if pd.notna(row.get('level')) else None,
            None,  # band (not directly in mercer)
            int(row.get('zone')) if pd.notna(row.get('zone')) else None,
            row.get('geography'),
            row.get('geography'),  # using geography as location
            row.get('market_segment'),
            row.get('industry'),
            None,  # company_count
            None,  # employee_count
            float(row.get('p10_salary')) if pd.notna(row.get('p10_salary')) else None,
            float(row.get('p25_salary')) if pd.notna(row.get('p25_salary')) else None,
            float(row.get('p50_salary')) if pd.notna(row.get('p50_salary')) else None,
            float(row.get('p75_salary')) if pd.notna(row.get('p75_salary')) else None,
            float(row.get('p90_salary')) if pd.notna(row.get('p90_salary')) else None,
            float(row.get('mean_salary')) if pd.notna(row.get('mean_salary')) else None,
            row.get('trend_indicator'),
            row.get('trend_velocity'),
            pd.to_datetime(row.get('data_date')).date() if pd.notna(row.get('data_date')) else None,
            row.get('currency', 'USD'),
            datetime.now(),  # created_at
            datetime.now(),  # updated_at
            None  # expires_at
        )
        records.append(record)

    # Insert query
    insert_query = """
        INSERT INTO compensation.benchmarks (
            id, source_type, source_file, job_family, job_code, job_title,
            level, band, zone, geography, location, market_segment, industry,
            company_count, employee_count, p10_salary, p25_salary, p50_salary,
            p75_salary, p90_salary, mean_salary, trend_indicator, trend_velocity,
            data_date, currency, created_at, updated_at, expires_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    execute_batch(cursor, insert_query, records)
    conn.commit()

    print(f"✓ Imported {len(records)} Mercer records")

    cursor.close()
    conn.close()

def import_lattice_data(filepath):
    """Import Lattice peer parity data"""
    print(f"Importing Lattice data from {filepath}...")

    df = pd.read_csv(filepath)
    conn = connect_db()
    cursor = conn.cursor()

    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        record = (
            str(uuid.uuid4()),  # id
            'lattice',  # source_type
            os.path.basename(filepath),  # source_file
            row.get('job_family'),
            None,  # job_code (not in lattice)
            row.get('job_title'),
            int(row.get('level')) if pd.notna(row.get('level')) else None,
            int(row.get('band')) if pd.notna(row.get('band')) else None,
            int(row.get('zone')) if pd.notna(row.get('zone')) else None,
            row.get('geography'),
            row.get('geography'),
            None,  # market_segment
            row.get('industry_segment'),
            int(row.get('company_count')) if pd.notna(row.get('company_count')) else None,
            int(row.get('employee_count')) if pd.notna(row.get('employee_count')) else None,
            float(row.get('p10_salary')) if pd.notna(row.get('p10_salary')) else None,
            float(row.get('p25_salary')) if pd.notna(row.get('p25_salary')) else None,
            float(row.get('p50_salary')) if pd.notna(row.get('p50_salary')) else None,
            float(row.get('p75_salary')) if pd.notna(row.get('p75_salary')) else None,
            float(row.get('p90_salary')) if pd.notna(row.get('p90_salary')) else None,
            float(row.get('mean_salary')) if pd.notna(row.get('mean_salary')) else None,
            None,  # trend_indicator
            None,  # trend_velocity
            pd.to_datetime(row.get('data_date')).date() if pd.notna(row.get('data_date')) else None,
            row.get('currency', 'USD'),
            datetime.now(),  # created_at
            datetime.now(),  # updated_at
            None  # expires_at
        )
        records.append(record)

    # Insert query (same as above)
    insert_query = """
        INSERT INTO compensation.benchmarks (
            id, source_type, source_file, job_family, job_code, job_title,
            level, band, zone, geography, location, market_segment, industry,
            company_count, employee_count, p10_salary, p25_salary, p50_salary,
            p75_salary, p90_salary, mean_salary, trend_indicator, trend_velocity,
            data_date, currency, created_at, updated_at, expires_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    execute_batch(cursor, insert_query, records)
    conn.commit()

    print(f"✓ Imported {len(records)} Lattice records")

    cursor.close()
    conn.close()

def verify_import():
    """Verify data was imported correctly"""
    conn = connect_db()
    cursor = conn.cursor()

    # Check record counts
    cursor.execute("""
        SELECT source_type, COUNT(*) as count
        FROM compensation.benchmarks
        GROUP BY source_type
    """)

    results = cursor.fetchall()
    print("\n📊 Import Summary:")
    print("-" * 30)
    for source, count in results:
        print(f"{source.title()}: {count:,} records")

    # Sample data check
    cursor.execute("""
        SELECT job_family, level, zone, p50_salary
        FROM compensation.benchmarks
        LIMIT 5
    """)

    print("\n🔍 Sample Records:")
    print("-" * 50)
    print(f"{'Job Family':<25} {'Level':<8} {'Zone':<6} {'P50 Salary':>12}")
    print("-" * 50)

    for row in cursor.fetchall():
        job_family = row[0] or 'N/A'
        level = row[1] if row[1] else 'N/A'
        zone = row[2] if row[2] else 'N/A'
        salary = f"${row[3]:,.0f}" if row[3] else 'N/A'
        print(f"{job_family:<25} {str(level):<8} {str(zone):<6} {salary:>12}")

    cursor.close()
    conn.close()

def main():
    """Main import function"""
    print("🚀 Starting data import to HRAnalyticsDB...")
    print("=" * 50)

    # Get data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    # Import Mercer data
    mercer_file = os.path.join(data_dir, 'mercer_benchmarks.csv')
    if os.path.exists(mercer_file):
        import_mercer_data(mercer_file)
    else:
        print(f"⚠️  Mercer file not found: {mercer_file}")

    # Import Lattice data
    lattice_file = os.path.join(data_dir, 'lattice_peer_parity.csv')
    if os.path.exists(lattice_file):
        import_lattice_data(lattice_file)
    else:
        print(f"⚠️  Lattice file not found: {lattice_file}")

    # Verify import
    verify_import()

    print("\n✅ Data import completed successfully!")

if __name__ == "__main__":
    main()