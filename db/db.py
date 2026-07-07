from datetime import datetime
from decimal import Decimal
import sqlite3
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


DATABASE_URL = "sqlite:///VPN_bot.db"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")
    vpn_keys: Mapped[list["VpnKey"]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "subs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    plan: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    user: Mapped[User] = relationship(back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="RUB")
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    invoice_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="payments")


class VpnKey(Base):
    __tablename__ = "vpn_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    key_data: Mapped[str] = mapped_column(Text, nullable=False)
    server_id: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="vpn_keys")


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _migrate_legacy_users_table():
    conn = sqlite3.connect("VPN_bot.db")
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cur.fetchone() is None:
        conn.close()
        return

    cur.execute("PRAGMA table_info(users)")
    columns = {row[1] for row in cur.fetchall()}

    if "telegram_id" in columns:
        conn.close()
        return

    cur.execute("ALTER TABLE users RENAME TO users_legacy")
    conn.commit()
    conn.close()

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        legacy_conn = sqlite3.connect("VPN_bot.db")
        legacy_cur = legacy_conn.cursor()
        legacy_cur.execute("SELECT id, name, user_name FROM users_legacy")
        rows = legacy_cur.fetchall()

        for row in rows:
            user = User(
                telegram_id=row[0],
                first_name=row[1],
                username=row[2],
            )
            session.add(user)

        session.commit()
        legacy_cur.execute("DROP TABLE users_legacy")
        legacy_conn.commit()
        legacy_conn.close()


def create_table():
    _migrate_legacy_users_table()
    Base.metadata.create_all(bind=engine)


def create_user(telegram_id, first_name, username):
    with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = session.execute(stmt).scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
            )
            session.add(user)
        else:
            user.first_name = first_name
            user.username = username

        session.commit()
        return user.id


def get_all_users():
    with SessionLocal() as session:
        users = session.execute(select(User).order_by(User.created_at.desc())).scalars().all()
        return [[user.telegram_id, user.first_name, user.username] for user in users]


def create_subscription(telegram_id, plan, started_at, expires_at, status="active"):
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user is None:
            return None

        sub = Subscription(
            user_id=user.id,
            plan=plan,
            started_at=started_at,
            expires_at=expires_at,
            status=status,
        )
        session.add(sub)
        session.commit()
        return sub.id


def create_payment(telegram_id, amount, currency="RUB", provider="manual", invoice_id=None, status="pending"):
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user is None:
            return None

        payment = Payment(
            user_id=user.id,
            amount=Decimal(str(amount)),
            currency=currency,
            provider=provider,
            invoice_id=invoice_id,
            status=status,
        )
        session.add(payment)
        session.commit()
        return payment.id


def create_vpn_key(telegram_id, key_data, server_id):
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user is None:
            return None

        vpn_key = VpnKey(user_id=user.id, key_data=key_data, server_id=server_id)
        session.add(vpn_key)
        session.commit()
        return vpn_key.id
