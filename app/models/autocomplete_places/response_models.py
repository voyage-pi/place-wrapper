from pydantic import BaseModel
from typing import List, Optional

class Suggestion(BaseModel):
    place_id: str
    text: str
    main_text: str
    secondary_text: Optional[str]

class Suggestions_List(BaseModel):
    suggestions_list: List[Suggestion]