from pydantic import BaseModel
from dotenv import dotenv_values


class BotConfig(BaseModel):
    """Bot env settings"""

    token: str
    admin_id: int | None


bot_config: BotConfig = BotConfig(**dotenv_values())
