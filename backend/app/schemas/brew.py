from pydantic import BaseModel, Field


class BrewCreateRequest(BaseModel):
    coffee_amount: float = Field(ge=12, le=25)
    grinder_setting_clicks: int = Field(ge=5, le=25)
    temperature_c: int = Field(ge=75, le=95)
    brew_time_seconds: int = Field(ge=60, le=300)
    press_time_seconds: int = Field(ge=10, le=120)
    anti_static_water_microliter: int = Field(ge=0, le=500)
    score: float = Field(ge=0, le=10)
    method: str = "median"
