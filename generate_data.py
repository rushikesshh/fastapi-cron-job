import random
from faker import Faker
from db_connection import get_connection

fake = Faker()

# Create a global database connection
conn = get_connection()
cursor = conn.cursor()

def create_tables():
    
    queries = {
        "dim_date": """
            CREATE TABLE dim_date (
                date_id SERIAL PRIMARY KEY,
                date_value DATE NOT NULL
            );
        """,
        "dim_region": """
            CREATE TABLE dim_region (
                region_id SERIAL PRIMARY KEY,
                region_name TEXT NOT NULL
            );
        """,
        "dim_age_group": """
            CREATE TABLE dim_age_group (
                age_id SERIAL PRIMARY KEY,
                age_range TEXT NOT NULL
            );
        """,
        "dim_gender": """
            CREATE TABLE dim_gender (
                gender_id SERIAL PRIMARY KEY,
                gender_name TEXT NOT NULL
            );
        """,
        "dim_platform": """
            CREATE TABLE dim_platform (
                platform_id SERIAL PRIMARY KEY,
                platform_name TEXT NOT NULL
            );
        """,
        "dim_placement": """
            CREATE TABLE dim_placement (
                placement_id SERIAL PRIMARY KEY,
                placement_name TEXT NOT NULL
            );
        """,
        "dim_device_type": """
            CREATE TABLE dim_device_type (
                device_type_id SERIAL PRIMARY KEY,
                device_type_name TEXT NOT NULL
            );
        """,
        "fact_ad_metrics_daily": """
            CREATE TABLE fact_ad_metrics_daily (
                date_id INT REFERENCES dim_date(date_id),
                region_id INT REFERENCES dim_region(region_id),
                age_id INT REFERENCES dim_age_group(age_id),
                gender_id INT REFERENCES dim_gender(gender_id),
                platform_id INT REFERENCES dim_platform(platform_id),
                placement_id INT REFERENCES dim_placement(placement_id),
                device_type_id INT REFERENCES dim_device_type(device_type_id),
                impressions INT,
                clicks INT,
                cost DECIMAL(10, 2),
                conversions INT,
                likes INT
            );
        """
    }

    for table, query in queries.items():
        print(f"Creating table: {table}...")
        cursor.execute(query)

    conn.commit()
    print("✅ Tables created successfully.")


def insert_data(table, columns, values):
    """Insert data into a given table using parameterized queries."""
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    try:
        cursor.executemany(query, values)
        conn.commit()
        print(f"✅ Data inserted successfully into {table}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting into {table}: {e}")
        raise


def generate_and_insert_dimensions():
    """Generate and insert data for dimension tables."""
    dim_date = [(i, f"2023-01-{i:02d}") for i in range(1, 32)]
    dim_region = [(1, "East"), (2, "West"), (3, "North"), (4, "South")]
    dim_age_group = [(1, "<18"), (2, "18-25"), (3, "26-35"), (4, "36-50"), (5, "50+")]
    dim_gender = [(1, "Male"), (2, "Female"), (3, "Other")]
    dim_platform = [(1, "Facebook"), (2, "Google Ads"), (3, "Instagram"), (4, "LinkedIn")]
    dim_placement = [(1, "Feed"), (2, "Stories"), (3, "Search"), (4, "Sidebar")]
    dim_device_type = [(1, "Mobile"), (2, "Desktop"), (3, "Tablet")]

    insert_data("dim_date", ["date_id", "date_value"], dim_date)
    insert_data("dim_region", ["region_id", "region_name"], dim_region)
    insert_data("dim_age_group", ["age_id", "age_range"], dim_age_group)
    insert_data("dim_gender", ["gender_id", "gender_name"], dim_gender)
    insert_data("dim_platform", ["platform_id", "platform_name"], dim_platform)
    insert_data("dim_placement", ["placement_id", "placement_name"], dim_placement)
    insert_data("dim_device_type", ["device_type_id", "device_type_name"], dim_device_type)

    print("✅ Dimension tables populated successfully!")


def generate_and_insert_fact_data():
    """Generate and insert random data into the fact table."""
    fact_ad_metrics = [
        (
            random.randint(1, 31),  # date_id
            random.randint(1, 4),  # region_id
            random.randint(1, 5),  # age_id
            random.randint(1, 3),  # gender_id
            random.randint(1, 4),  # platform_id
            random.randint(1, 4),  # placement_id
            random.randint(1, 3),  # device_type_id
            random.randint(1000, 10000),  # impressions
            random.randint(100, 1000),  # clicks
            round(random.uniform(10, 500), 2),  # cost
            random.randint(0, 200),  # conversions
            random.randint(0, 500)  # likes
        )
        for _ in range(1000)
    ]

    insert_data(
        "fact_ad_metrics_daily",
        ["date_id", "region_id", "age_id", "gender_id", "platform_id",
         "placement_id", "device_type_id", "impressions", "clicks", "cost",
         "conversions", "likes"],
        fact_ad_metrics
    )

    print("✅ Fact table populated successfully!")


if __name__ == "__main__":
    print("🚀 Starting table creation...")

    try:
        create_tables()
        generate_and_insert_dimensions()
        generate_and_insert_fact_data()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Ensure proper cleanup
        cursor.close()
        conn.close()
