from pydantic import BaseModel, field_validator
from enum import Enum


class ProjectType(str, Enum):
    APPLIED = "applied"
    RESEARCH = "research"
    BUSINESS = "business"

# изменить в будущем
STAGE_MAPPING = {
    ProjectType.APPLIED: ["requirement_analysis", "design", "implementation", "testing", "deployment"], # жц
    ProjectType.RESEARCH: ["planning", "research", "implementation"], #  фазы
    ProjectType.BUSINESS: ["market_research", "business_plan", "funding", "launch", "scaling"], # этапы
}


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    type: ProjectType
    stage: str | None = None

    @field_validator("stage")
    def validate_stage(cls, v, values):
        if "type" not in values:
            raise ValueError("Project type must be set before stage validation")
        
        allowed_stages = STAGE_MAPPING[values["type"]]
        if v is None:
            return allowed_stages[0]
        if v not in allowed_stages:
            raise ValueError(f"Invalid stage for project type {values['type']}. Allowed: {allowed_stages}")
        return v


class ProjectResponse(ProjectBase):
    id: int
    type: ProjectType
    stage: str
