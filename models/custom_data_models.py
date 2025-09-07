from sqlalchemy.orm import mapped_column, Mapped

from models import BaseModel, BaseModelMixin, Json


class CustomData(BaseModel, BaseModelMixin):
    __tablename__ = 'custom_data'

    name: Mapped[str] = mapped_column(nullable=False, unique=False)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    data: Mapped[dict | list] = mapped_column(Json(), nullable=True)  # type: ignore[arg-type]
