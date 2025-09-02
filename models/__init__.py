import json
from datetime import datetime, UTC

from sqlalchemy import TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.types import String, DateTime


class AwareDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            raise ValueError("Naive date-times not allowed")
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class SnowflakeID(TypeDecorator):
    impl = String(30)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return int(value) if value is not None else None


class Json(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None


class BaseModel(DeclarativeBase):
    pass


class BaseModelMixin:

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                 default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                 default=datetime.now(UTC),
                                                 onupdate=datetime.now(UTC))
