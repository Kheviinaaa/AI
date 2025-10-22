from pydantic import BaseModel
from typing import List, Optional

class Constraint(BaseModel):
    stories_per_epic_min: Optional[int] = 1
    stories_per_epic_max: Optional[int] = 3
    tests_per_story_min: Optional[int] = 1
    tests_per_story_max: Optional[int] = 3

class EpicIn(BaseModel):
    epic_id: str
    title: str
    description: Optional[str] = ""

class GenerateRequest(BaseModel):
    project_name: str
    epics: List[EpicIn]
    constraints: Optional[Constraint] = None
