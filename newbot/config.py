from dataclasses import dataclass, field
import os


@dataclass(slots=True)
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: list[int] = field(
        default_factory=lambda: [
            int(x) for x in os.getenv("ADMIN_IDS", "").split()
        ]
        if os.getenv("ADMIN_IDS")
        else []
    )
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./gamify.db"
    )


config = Config()
