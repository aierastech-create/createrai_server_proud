from pydantic import BaseModel, Field
from enum import Enum


class FeatureType(str, Enum):
    IDEA = "idea"
    TITLE = "title"
    SCRIPT = "script"
    SEO = "seo"


class GenerateRequest(BaseModel):
    feature: FeatureType = Field(
        ...,
        description="AI feature to use: idea, title, script, or seo"
    )
    input: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User input / topic for content generation"
    )


class GenerateResponse(BaseModel):
    status: str = "success"
    feature: str
    data: str
