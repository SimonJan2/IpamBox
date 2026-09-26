from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocsPageCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    # Optional explicit slug — slugified server-side either way; collisions
    # get a -2/-3/… suffix so creates never 409 on naming.
    slug: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=64)
    body: str = ""


class DocsPageUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    # An explicit slug on PATCH is an intentional rename — collision → 409.
    slug: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=64)
    body: str | None = None


class DocsPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    category: str
    body: str
    created_by: str | None
    created_at: datetime
    updated_at: datetime
