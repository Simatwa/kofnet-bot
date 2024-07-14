from pydantic import BaseModel, HttpUrl, field_validator
from dotenv import dotenv_values


class BotConfig(BaseModel):
    """Bot env settings"""

    token: str
    admin_id: int | None = None
    channel_id: int | None = None
    channel_url: HttpUrl | None = None
    force_sub: bool = False


bot_config: BotConfig = BotConfig(**dotenv_values())
