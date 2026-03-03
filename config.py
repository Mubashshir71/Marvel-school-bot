import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: set[int]
    operator_phone: str
    location_text: str

def load_config() -> Config:
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN .env ichida yo‘q")

    admin_raw = (os.getenv("ADMIN_IDS") or "").strip()
    admin_ids: set[int] = set()
    if admin_raw:
        for x in admin_raw.split(","):
            x = x.strip()
            if x.isdigit():
                admin_ids.add(int(x))

    operator_phone = (os.getenv("OPERATOR_PHONE") or "+998 XX XXX XX XX").strip()
    location_text = (os.getenv("LOCATION_TEXT") or "Hoshshing").strip()

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        operator_phone=operator_phone,
        location_text=location_text,
    )