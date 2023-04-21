from pydantic import Field

from tekst.config import InfoConfig, TekstConfig, TekstInfoConfig, get_config
from tekst.layer_types import LayerTypeInfo
from tekst.models.common import ModelBase
from tekst.models.settings import PlatformSettingsRead
from tekst.models.text import TextRead


_cfg: TekstConfig = get_config()


class PlatformSecurityInfo(ModelBase):
    users_active_by_default: bool = _cfg.security.users_active_by_default
    users_need_verification: bool = _cfg.security.users_need_verification
    enable_registration: bool = _cfg.security.enable_registration
    enable_cookie_auth: bool = _cfg.security.enable_cookie_auth


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    info: InfoConfig = _cfg.info
    tekst_info: TekstInfoConfig = _cfg.tekst_info
    texts: list[TextRead]
    settings: PlatformSettingsRead
    security: PlatformSecurityInfo = Field(default_factory=PlatformSecurityInfo)
    layer_types: list[LayerTypeInfo]
