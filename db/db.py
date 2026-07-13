from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "sqlite+aiosqlite:///vpn_bot.db"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def init_db():
    # import models so Base.metadata knows about all tables
    import db.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(text("PRAGMA table_info(payments)"))
        columns = {row[1] for row in result.fetchall()}
        if "paid_at" not in columns:
            await conn.execute(text("ALTER TABLE payments ADD COLUMN paid_at DATETIME"))
        if "renew_at" not in columns:
            await conn.execute(text("ALTER TABLE payments ADD COLUMN renew_at DATETIME"))

        required_paid_users_columns = {
            "id",
            "telegram_id",
            "username",
            "tariff",
            "status",
            "started_at",
            "expires_at",
            "warned_3_at",
            "warned_2_at",
            "warned_1_at",
            "warned_0_at",
            "created_at",
        }
        result = await conn.execute(text("PRAGMA table_info(paid_users)"))
        paid_users_columns = {row[1] for row in result.fetchall()}
        old_table_result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='paid_users_old'")
        )
        old_table_exists = old_table_result.fetchone() is not None

        if paid_users_columns and ("vpn_link" in paid_users_columns or not required_paid_users_columns.issubset(paid_users_columns)):
            await conn.execute(text("ALTER TABLE paid_users RENAME TO paid_users_old"))
            old_table_exists = True
            paid_users_columns = set()

        if not paid_users_columns:
            await conn.execute(text(
                """
                CREATE TABLE IF NOT EXISTS paid_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    username VARCHAR,
                    tariff VARCHAR NOT NULL,
                    status VARCHAR NOT NULL DEFAULT 'ACTIVE',
                    started_at DATETIME,
                    expires_at DATETIME,
                    warned_3_at DATETIME,
                    warned_2_at DATETIME,
                    warned_1_at DATETIME,
                    warned_0_at DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            ))

        if old_table_exists:
            paid_users_count = await conn.execute(text("SELECT COUNT(*) FROM paid_users"))
            if paid_users_count.scalar_one() == 0:
                old_columns_result = await conn.execute(text("PRAGMA table_info(paid_users_old)"))
                old_columns = {row[1] for row in old_columns_result.fetchall()}

                if {"current_tariff", "current_status", "first_paid_at", "last_paid_at", "renew_at"}.issubset(old_columns):
                    await conn.execute(text(
                        """
                        INSERT INTO paid_users (
                            telegram_id,
                            username,
                            tariff,
                            status,
                            started_at,
                            expires_at,
                            warned_3_at,
                            warned_2_at,
                            warned_1_at,
                            warned_0_at,
                            created_at
                        )
                        SELECT
                            telegram_id,
                            NULL,
                            COALESCE(current_tariff, ''),
                            COALESCE(current_status, 'ACTIVE'),
                            last_paid_at,
                            renew_at,
                            NULL,
                            NULL,
                            NULL,
                            NULL,
                            COALESCE(first_paid_at, CURRENT_TIMESTAMP)
                        FROM paid_users_old
                        """
                    ))
                elif {"tariff", "status", "started_at", "expires_at", "vpn_link", "created_at"}.issubset(old_columns):
                    await conn.execute(text(
                        """
                        INSERT INTO paid_users (
                            telegram_id,
                            username,
                            tariff,
                            status,
                            started_at,
                            expires_at,
                            warned_3_at,
                            warned_2_at,
                            warned_1_at,
                            warned_0_at,
                            created_at
                        )
                        SELECT
                            telegram_id,
                            NULL,
                            tariff,
                            COALESCE(status, 'ACTIVE'),
                            started_at,
                            expires_at,
                            NULL,
                            NULL,
                            NULL,
                            NULL,
                            COALESCE(created_at, CURRENT_TIMESTAMP)
                        FROM paid_users_old
                        """
                    ))

            await conn.execute(text("DROP TABLE paid_users_old"))

        if "username" not in paid_users_columns and paid_users_columns:
            await conn.execute(text("ALTER TABLE paid_users ADD COLUMN username VARCHAR"))
        if "warned_3_at" not in paid_users_columns and paid_users_columns:
            await conn.execute(text("ALTER TABLE paid_users ADD COLUMN warned_3_at DATETIME"))
        if "warned_2_at" not in paid_users_columns and paid_users_columns:
            await conn.execute(text("ALTER TABLE paid_users ADD COLUMN warned_2_at DATETIME"))
        if "warned_1_at" not in paid_users_columns and paid_users_columns:
            await conn.execute(text("ALTER TABLE paid_users ADD COLUMN warned_1_at DATETIME"))
        if "warned_0_at" not in paid_users_columns and paid_users_columns:
            await conn.execute(text("ALTER TABLE paid_users ADD COLUMN warned_0_at DATETIME"))

        await conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS bot_visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL UNIQUE,
                username VARCHAR,
                first_name VARCHAR,
                visits_count INTEGER NOT NULL DEFAULT 1,
                first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        ))

        result = await conn.execute(text("PRAGMA table_info(bot_visitors)"))
        bot_visitors_columns = {row[1] for row in result.fetchall()}

        if "username" not in bot_visitors_columns:
            await conn.execute(text("ALTER TABLE bot_visitors ADD COLUMN username VARCHAR"))
        if "first_name" not in bot_visitors_columns:
            await conn.execute(text("ALTER TABLE bot_visitors ADD COLUMN first_name VARCHAR"))
        if "visits_count" not in bot_visitors_columns:
            await conn.execute(text("ALTER TABLE bot_visitors ADD COLUMN visits_count INTEGER NOT NULL DEFAULT 1"))
        if "first_seen_at" not in bot_visitors_columns:
            await conn.execute(text("ALTER TABLE bot_visitors ADD COLUMN first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
        if "last_seen_at" not in bot_visitors_columns:
            await conn.execute(text("ALTER TABLE bot_visitors ADD COLUMN last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))


def _renew_days_from_tariff(tariff: str) -> int | None:
    tariff_lower = tariff.lower()
    if "7 дней" in tariff_lower:
        return 7
    if "1 месяц" in tariff_lower:
        return 30
    if "3 месяца" in tariff_lower:
        return 90
    if "6 месяцев" in tariff_lower:
        return 180
    if "12 месяцев" in tariff_lower:
        return 365
    return None


async def save_payment(transaction_id: str, telegram_id: int, tariff: str, amount: int) -> None:
    from db.models import Payment
    async with AsyncSessionLocal() as session:
        payment = Payment(
            transaction_id=transaction_id,
            telegram_id=telegram_id,
            tariff=tariff,
            amount=amount,
            status="PENDING",
        )
        session.add(payment)
        await session.commit()


async def get_payment(transaction_id: str):
    from db.models import Payment
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()


async def update_payment_status(transaction_id: str, status: str) -> bool:
    from db.models import Payment
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return False

        if status == "CONFIRMED" and payment.status == "CONFIRMED":
            return False

        payment.status = status
        if status == "CONFIRMED":
            paid_at = datetime.utcnow()
            payment.paid_at = paid_at
            renew_days = _renew_days_from_tariff(payment.tariff)
            if renew_days is not None:
                payment.renew_at = paid_at + timedelta(days=renew_days)

        await session.commit()
        return True


async def upsert_paid_user_from_payment(transaction_id: str, username: str | None = None) -> None:
    from db.models import PaidUser, Payment

    async with AsyncSessionLocal() as session:
        payment_result = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        payment = payment_result.scalar_one_or_none()
        if not payment or payment.status != "CONFIRMED":
            return

        user_result = await session.execute(
            select(PaidUser).where(PaidUser.telegram_id == payment.telegram_id)
        )
        paid_user = user_result.scalar_one_or_none()

        paid_at = payment.paid_at or datetime.utcnow()

        if paid_user is None:
            paid_user = PaidUser(
                telegram_id=payment.telegram_id,
                username=username,
                tariff=payment.tariff,
                status="ACTIVE",
                started_at=paid_at,
                expires_at=payment.renew_at,
                warned_3_at=None,
                warned_2_at=None,
                warned_1_at=None,
                warned_0_at=None,
            )
            session.add(paid_user)
        else:
            if username is not None:
                paid_user.username = username
            paid_user.tariff = payment.tariff
            paid_user.status = "ACTIVE"
            paid_user.started_at = paid_at
            paid_user.expires_at = payment.renew_at
            paid_user.warned_3_at = None
            paid_user.warned_2_at = None
            paid_user.warned_1_at = None
            paid_user.warned_0_at = None

        await session.commit()


async def list_paid_users():
    from db.models import PaidUser

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PaidUser))
        return result.scalars().all()


async def get_paid_user(telegram_id: int):
    from db.models import PaidUser

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PaidUser).where(PaidUser.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_user_payments(telegram_id: int, limit: int = 5):
    from db.models import Payment

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Payment)
            .where(Payment.telegram_id == telegram_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def mark_paid_user_warning(telegram_id: int, days_left: int) -> bool:
    from db.models import PaidUser

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PaidUser).where(PaidUser.telegram_id == telegram_id)
        )
        paid_user = result.scalar_one_or_none()
        if not paid_user:
            return False

        now = datetime.utcnow()
        if days_left == 3 and paid_user.warned_3_at is None:
            paid_user.warned_3_at = now
        elif days_left == 2 and paid_user.warned_2_at is None:
            paid_user.warned_2_at = now
        elif days_left == 1 and paid_user.warned_1_at is None:
            paid_user.warned_1_at = now
        elif days_left == 0 and paid_user.warned_0_at is None:
            paid_user.warned_0_at = now
        else:
            return False

        await session.commit()
        return True


async def mark_paid_user_expired(telegram_id: int) -> bool:
    from db.models import PaidUser

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PaidUser).where(PaidUser.telegram_id == telegram_id)
        )
        paid_user = result.scalar_one_or_none()
        if paid_user and paid_user.status != "EXPIRED":
            paid_user.status = "EXPIRED"
            await session.commit()
            return True

        return False


async def register_bot_visit(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> None:
    from db.models import BotVisitor

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BotVisitor).where(BotVisitor.telegram_id == telegram_id)
        )
        visitor = result.scalar_one_or_none()

        now = datetime.utcnow()
        if visitor is None:
            visitor = BotVisitor(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                visits_count=1,
                first_seen_at=now,
                last_seen_at=now,
            )
            session.add(visitor)
        else:
            visitor.username = username
            visitor.first_name = first_name
            visitor.visits_count += 1
            visitor.last_seen_at = now

        await session.commit()


async def get_bot_visitors_count() -> int:
    from db.models import BotVisitor

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(BotVisitor.id)))
        return int(result.scalar_one() or 0)


async def has_used_free_trial(telegram_id: int) -> bool:
    from db.models import FreeTrialUsage

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(FreeTrialUsage).where(FreeTrialUsage.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none() is not None


async def activate_free_trial(telegram_id: int, username: str | None = None) -> bool:
    from db.models import FreeTrialUsage, PaidUser

    async with AsyncSessionLocal() as session:
        used = FreeTrialUsage(telegram_id=telegram_id)
        session.add(used)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            return False

        now = datetime.utcnow()
        expires_at = now + timedelta(days=3)

        paid_user_result = await session.execute(
            select(PaidUser).where(PaidUser.telegram_id == telegram_id)
        )
        paid_user = paid_user_result.scalar_one_or_none()

        if paid_user is None:
            paid_user = PaidUser(
                telegram_id=telegram_id,
                username=username,
                tariff="3 дня бесплатно",
                status="ACTIVE",
                started_at=now,
                expires_at=expires_at,
                warned_3_at=None,
                warned_2_at=None,
                warned_1_at=None,
                warned_0_at=None,
            )
            session.add(paid_user)
        else:
            paid_user.username = username
            paid_user.tariff = "3 дня бесплатно"
            paid_user.status = "ACTIVE"
            paid_user.started_at = now
            paid_user.expires_at = expires_at
            paid_user.warned_3_at = None
            paid_user.warned_2_at = None
            paid_user.warned_1_at = None
            paid_user.warned_0_at = None

        await session.commit()
        return True