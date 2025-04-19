from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List, Tuple


class Paint(BaseModel):
    """
    """

    name: str = Field(
        ...,
        description="""
        aa.
        """,
    )

    price: Optional[str] = Field(
        default=None,
        description="""
        aa.
        """,
    )

    tags: List[str] = Field(
        default=[],
        description="""
        aa.
        """,
    )

    image_url: Optional[str] = Field(
        default=None,
        description="""
        aa.
        """,
    )

    rgb_color: Optional[Tuple[int, int, int]] = Field(
        default=None,
        description="RGB color extracted from the image (center pixel)."
    )

    hex_color: Optional[str] = Field(
        default=None,
        description="HEX color code extracted from the image (center pixel)."
    )