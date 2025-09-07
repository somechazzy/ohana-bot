from sqlalchemy import select, update

from models.custom_data_models import CustomData
from repositories import BaseRepo


class CustomDataRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_custom_data(self,
                                 name: str,
                                 code: str,
                                 data: dict | list) -> CustomData:
        """
        Create a custom data record.
        """
        new_record = CustomData(
            name=name,
            code=code,
            data=data
        )
        self._session.add(new_record)
        await self._session.flush()
        return new_record

    async def get_custom_data(self, code: str) -> CustomData | None:
        """
        Retrieve custom data by its unique code.
        """
        query = select(CustomData).where(CustomData.code == code)
        return (await self._session.execute(query)).unique().scalar_one_or_none()

    async def update_custom_data(self, code: str, **update_data) -> None:
        """
        Update custom data by its unique code.
        """
        await self._session.execute(
            update(CustomData).where(CustomData.code == code).values(**update_data)
        )
        await self._session.flush()
