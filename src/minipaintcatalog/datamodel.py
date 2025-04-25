from pydantic import BaseModel, Field
from typing import Optional


class Paint(BaseModel):
    """
    The data model for a paint used to paint miniatures.
    """

    manufacturer: str = Field(
        ...,
        description="The name of the manufacturer or vendor: Citadel, Vallejo, etc.",
    )

    name: str = Field(
        ...,
        description="The name of the painting as defined for the manufacturer",
    )

    price: Optional[str] = Field(
        default=None,
        description="The price in dollars.",
    )

    image_url: Optional[str] = Field(
        default=None,
        description="The URL to the image in the manufacturer website (if it exists). Useful to determine the RGB/HEX code for the color.",
    )

    rgb_color: Optional[tuple[int, int, int]] = Field(
        default=None,
        description="RGB color extracted from the image (center pixel)."
    )

    hex_color: Optional[str] = Field(
        default=None,
        description="HEX color code extracted from the image (center pixel)."
    )