from urllib.parse import unquote
from typing import List, Optional
from datetime import date, datetime
from scheduler import start_scheduler
from db_connection import get_connection  
from pydantic import BaseModel, Field, validator
from fastapi import FastAPI, Query, HTTPException, Depends
from model import QueryParams, parse_comma_separated_string


app = FastAPI()
start_scheduler()
conn = get_connection()
cursor = conn.cursor()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running with Asynchronous and Non-Blocking APScheduler!"}


@app.get("/fetch-data/")
def fetch_data(params: QueryParams = Depends()):
    """
    Fetch data from fact_ad_metrics_daily with optional filters.
    All filters support multiple selections.
    """
    params.validate_dates()

    # Parse comma-separated strings into lists of strings
    region_list = parse_comma_separated_string(params.region)
    age_group_list = parse_comma_separated_string(params.age_group)
    gender_list = parse_comma_separated_string(params.gender)
    platform_list = parse_comma_separated_string(params.platform)
    placement_list = parse_comma_separated_string(params.placement)
    device_type_list = parse_comma_separated_string(params.device_type)

    query = """
        SELECT 
            f.date_id, d.date_value, 
            r.region_name, 
            a.age_range, 
            g.gender_name, 
            p.platform_name, 
            pl.placement_name, 
            dt.device_type_name, 
            f.impressions, f.clicks, f.cost, f.conversions, f.likes
        FROM fact_ad_metrics_daily f
        JOIN dim_date d ON f.date_id = d.date_id
        JOIN dim_region r ON f.region_id = r.region_id
        JOIN dim_age_group a ON f.age_id = a.age_id
        JOIN dim_gender g ON f.gender_id = g.gender_id
        JOIN dim_platform p ON f.platform_id = p.platform_id
        JOIN dim_placement pl ON f.placement_id = pl.placement_id
        JOIN dim_device_type dt ON f.device_type_id = dt.device_type_id
        WHERE 1=1
    """

    params_list = []

    if params.start_date:
        query += " AND d.date_value >= %s"
        params_list.append(params.start_date)

    if params.end_date:
        query += " AND d.date_value <= %s"
        params_list.append(params.end_date)

    if region_list:
        query += " AND r.region_name = ANY(%s)"
        params_list.append(region_list)

    if age_group_list:
        query += " AND a.age_range = ANY(%s)"
        params_list.append(age_group_list)

    if gender_list:
        query += " AND g.gender_name = ANY(%s)"
        params_list.append(gender_list)

    if platform_list:
        query += " AND p.platform_name = ANY(%s)"
        params_list.append(platform_list)

    if placement_list:
        query += " AND pl.placement_name = ANY(%s)"
        params_list.append(placement_list)

    if device_type_list:
        query += " AND dt.device_type_name = ANY(%s)"
        params_list.append(device_type_list)

    try:
        cursor.execute(query, params_list)
        data = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
    

    result = [
        {
            "date": row[1],
            "region": row[2],
            "age_group": row[3],
            "gender": row[4],
            "platform": row[5],
            "placement": row[6],
            "device_type": row[7],
            "impressions": row[8],
            "clicks": row[9],
            "cost": float(row[10]),
            "conversions": row[11],
            "likes": row[12],
        }
        for row in data
    ]

    return {"data": result}


@app.on_event("shutdown")
def shutdown():
    """Close the database connection when API stops."""
    conn.close()

