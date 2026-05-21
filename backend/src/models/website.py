from datetime import datetime

from pydantic import BaseModel


class Website(BaseModel):
    url: str | None = None
    extracted_at: datetime
    last_checked: datetime | None = None
    accessible: bool | None = None
