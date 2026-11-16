from sqlalchemy import text

from app.core.database import engine, Base
from app.db.models import User, DokumenUpload, DrafKebutuhan, AuditKebutuhan, TemuanCacat, HistoryDownload, PasswordResetToken

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Task 06: create_all does not ALTER pre-existing tables. Add the new
    # evaluator columns idempotently so existing databases keep working.
    async with engine.begin() as conn:
        await _ensure_audit_columns(conn)


async def _ensure_audit_columns(conn):
    is_sqlite = engine.url.drivername.startswith("sqlite")
    if is_sqlite:
        res = await conn.execute(text("PRAGMA table_info(audit_kebutuhan)"))
        cols = {row[1] for row in res.fetchall()}
        if "evaluator" not in cols:
            await conn.execute(text(
                "ALTER TABLE audit_kebutuhan ADD COLUMN evaluator VARCHAR(20) "
                "NOT NULL DEFAULT 'rule_based'"
            ))
        if "model_version" not in cols:
            await conn.execute(text(
                "ALTER TABLE audit_kebutuhan ADD COLUMN model_version VARCHAR(80)"
            ))
    else:
        # PostgreSQL: rely on IF NOT EXISTS-style handling via exception
        for ddl in (
            "ALTER TABLE audit_kebutuhan ADD COLUMN evaluator VARCHAR(20) NOT NULL DEFAULT 'rule_based'",
            "ALTER TABLE audit_kebutuhan ADD COLUMN model_version VARCHAR(80)",
        ):
            try:
                await conn.execute(text(ddl))
            except Exception:
                pass  # column already exists
