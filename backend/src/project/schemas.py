from pydantic import BaseModel
from enum import Enum


class ProjectType(str, Enum):
    applied = "applied"
    research = "research"
    business = "business"