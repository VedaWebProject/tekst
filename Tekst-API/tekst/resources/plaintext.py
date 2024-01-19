from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import DeepLLinksConfig, ResourceConfigBase
from tekst.models.unit import UnitBase
from tekst.resources import ResourceTypeABC


class Plaintext(ResourceTypeABC):
    """A simple plaintext resource type"""

    @classmethod
    def resource_model(cls) -> type["PlaintextResource"]:
        return PlaintextResource

    @classmethod
    def unit_model(cls) -> type["PlaintextUnit"]:
        return PlaintextUnit


class PlaintextResourceConfig(ResourceConfigBase):
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlaintextResource(ResourceBase):
    resource_type: Literal["plaintext"]  # snake_cased resource type classname
    config: PlaintextResourceConfig = PlaintextResourceConfig()


class PlaintextUnit(UnitBase):
    """A unit of a plaintext resource"""

    resource_type: Literal["plaintext"]  # snake_cased resource type classname
    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400, strip_whitespace=True),
        Field(
            description="Text content of the plaintext unit",
        ),
    ]