from urllib.parse import unquote
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException



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
