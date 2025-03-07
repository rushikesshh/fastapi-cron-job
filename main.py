from urllib.parse import unquote
from typing import List, Optional
from datetime import date, datetime
from scheduler import start_scheduler
from db_connection import get_connection  
from pydantic import BaseModel, Field, validator
from fastapi import FastAPI, Query, HTTPException, Depends



app = FastAPI()
start_scheduler()
conn = get_connection()
cursor = conn.cursor()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running with Asynchronous and Non-Blocking APScheduler!"}


def parse_comma_separated_string(input_value: Optional[str]) -> Optional[List[str]]:
    """
    Parse a comma-separated string into a list of strings.
    Handles both single values and comma-separated values.
    Example: "Male,Female" -> ["Male", "Female"]
    Example: "Male%2CFemale" -> ["Male", "Female"]
    """
    if not input_value:
        return None

    # Decode URL-encoded characters (e.g., %2C -> ,)
    decoded_str = unquote(input_value)
    # Split by comma and strip whitespace
    return [item.strip() for item in decoded_str.split(",")]


class QueryParams(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date for filtering data")
    end_date: Optional[str] = Field(None, description="End date for filtering data")
    region: Optional[str] = Field(None, description="Comma-separated region names")
    age_group: Optional[str] = Field(None, description="Comma-separated age groups")
    gender: Optional[str] = Field(None, description="Comma-separated gender values")
    platform: Optional[str] = Field(None, description="Comma-separated platforms")
    placement: Optional[str] = Field(None, description="Comma-separated placements")
    device_type: Optional[str] = Field(None, description="Comma-separated device types")

    def validate_dates(self):
        """Ensures that start_date is before end_date."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise HTTPException(status_code=400, detail="start_date cannot be after end_date")
        if self.start_date:
            try:
                start_date_obj = datetime.strptime(self.start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {self.start_date}. Expected format: YYYY-MM-DD.")
        if self.end_date:
            try:
                end_date_obj = datetime.strptime(self.end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {self.end_date}. Expected format: YYYY-MM-DD.")
        
    @validator("region")
    def validate_region(cls, value):
        """Validates that region contains only allowed values."""
        if value:
            regions = parse_comma_separated_string(value)
            ALLOWED_REGIONS = ["East","West","North","South"]
            invalid_groups = [age for age in regions if age not in ALLOWED_REGIONS]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid region values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_REGIONS)}"
                )
        return value
    
    @validator("age_group")
    def validate_age_group(cls, value):
        """Validates that age_group contains only allowed values."""
        if value:
            age_groups = parse_comma_separated_string(value)
            ALLOWED_AGE_GROUPS = ["<18","18-25","26-35","36-50","50+"]
            invalid_groups = [age for age in age_groups if age not in ALLOWED_AGE_GROUPS]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid age_group values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_AGE_GROUPS)}"
                )
        return value
    
    @validator("gender")
    def validate_gender(cls, value):
        """Validates that gender contains only allowed values."""
        if value:
            genders = parse_comma_separated_string(value)
            ALLOWED_GENDERS = ["Male","Female","Other"]
            invalid_groups = [age for age in genders if age not in ALLOWED_GENDERS]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid genders values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_GENDERS)}"
                )
        return value
    
    @validator("platform")
    def validate_platform(cls, value):
        """Validates that platform contains only allowed values."""
        if value:
            platforms = parse_comma_separated_string(value)
            ALLOWED_PLATFORMS = ["Facebook", "Google Ads", "Instagram", "LinkedIn"]
            invalid_groups = [age for age in platforms if age not in ALLOWED_PLATFORMS]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid platforms values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_PLATFORMS)}"
                )
        return value
    
    @validator("placement")
    def validate_placement(cls, value):
        """Validates that placement contains only allowed values."""
        if value:
            placements = parse_comma_separated_string(value)
            ALLOWED_PLACEMENTS = ["Feed", "Stories", "Search", "Sidebar"]
            invalid_groups = [age for age in placements if age not in ALLOWED_PLACEMENTS]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid placements values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_PLACEMENTS)}"
                )
        return value
    
    @validator("device_type")
    def validate_device_type(cls, value):
        """Validates that device_type contains only allowed values."""
        if value:
            device_types = parse_comma_separated_string(value)
            ALLOWED_DEVICE_TYPES = ["Mobile", "Desktop", "Tablet"]
            invalid_groups = [age for age in device_types if age not in ALLOWED_DEVICE_TYPES]
            if invalid_groups:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid device_types values: {', '.join(invalid_groups)}. Allowed values are: {', '.join(ALLOWED_DEVICE_TYPES)}"
                )
        return value
    


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

