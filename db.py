import aiosqlite
from typing import Optional, Any

DB_PATH = "marvel_school.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER NOT NULL,
    username TEXT,
    full_name TEXT,
    course TEXT NOT NULL,
    goal TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    phone TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    note TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
"""

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_SQL)
        await db.commit()

async def add_lead(
    tg_user_id: int,
    username: Optional[str],
    full_name: str,
    course: str,
    goal: str,
    time_slot: str,
    phone: str,
    created_at: str
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO leads (tg_user_id, username, full_name, course, goal, time_slot, phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tg_user_id, username, full_name, course, goal, time_slot, phone, created_at),
        )
        await db.commit()
        return cur.lastrowid

async def get_lead(lead_id: int) -> Optional[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM leads WHERE id=?", (lead_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

async def list_leads(status: Optional[str] = None, limit: int = 20) -> list[dict[str, Any]]:
    q = "SELECT id, tg_user_id, username, full_name, course, goal, time_slot, phone, status, note, created_at FROM leads"
    params: list[Any] = []
    if status:
        q += " WHERE status = ?"
        params.append(status)
    q += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(q, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

async def set_status(lead_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
        await db.commit()

async def set_note(lead_id: int, note: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE leads SET note=? WHERE id=?", (note, lead_id))
        await db.commit()

async def distinct_user_ids(limit: int = 20000) -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT DISTINCT tg_user_id FROM leads ORDER BY tg_user_id DESC LIMIT ?", (limit,))
        rows = await cur.fetchall()
        return [int(r[0]) for r in rows]

async def count_stats() -> dict[str, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async def _count(where: str = "") -> int:
            q = "SELECT COUNT(*) FROM leads"
            if where:
                q += " WHERE " + where
            cur = await db.execute(q)
            (n,) = await cur.fetchone()
            return int(n)

        return {
            "all": await _count(),
            "new": await _count("status='new'"),
            "contacted": await _count("status='contacted'"),
            "lost": await _count("status='lost'"),
        }