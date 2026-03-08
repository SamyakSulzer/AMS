from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from database.mappers.master_map import MasterKey, MasterValue

class MasterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Master Key Operations ---

    async def create_key(self, key_name: str, is_active: bool = True) -> MasterKey:
        key = MasterKey(key_name=key_name, is_active=is_active, is_deleted=False)
        self.session.add(key)
        await self.session.commit()
        await self.session.refresh(key)
        return key

    async def get_key(self, key_id: int) -> MasterKey | None:
        result = await self.session.execute(select(MasterKey).where(MasterKey.id == key_id))
        return result.scalar_one_or_none()

    async def list_keys(
        self, skip: int = 0, limit: int = 100, sort_by: str = "id", order: str = "asc"
    ) -> list[MasterKey]:
        query = select(MasterKey).where(MasterKey.is_deleted == False)
        
        if hasattr(MasterKey, sort_by):
            col = getattr(MasterKey, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))
                
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_keys(self) -> int:
        query = select(func.count()).select_from(MasterKey).where(MasterKey.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update_key(self, key_id: int, **kwargs) -> MasterKey | None:
        key = await self.get_key(key_id)
        if key:
            for k, v in kwargs.items():
                if v is not None and hasattr(key, k):
                    setattr(key, k, v)
            await self.session.commit()
            await self.session.refresh(key)
        return key

    async def delete_key(self, key_id: int) -> bool:
        # Soft delete
        key = await self.get_key(key_id)
        if key:
            key.is_deleted = True
            await self.session.commit()
            return True
        return False

    # --- Master Value Operations ---

    async def create_value(
        self, key_id: int, value: list[str], order_id: int | None = None, is_active: bool = True
    ) -> MasterValue:
        val = MasterValue(
            key_id=key_id,
            value=value,
            order_id=order_id,
            is_active=is_active,
            is_deleted=False
        )
        self.session.add(val)
        await self.session.commit()
        await self.session.refresh(val)
        return val

    async def get_value(self, value_id: int) -> MasterValue | None:
        result = await self.session.execute(select(MasterValue).where(MasterValue.id == value_id))
        return result.scalar_one_or_none()

    async def list_values(
        self, skip: int = 0, limit: int = 100, sort_by: str = "id", order: str = "asc", key_id: int | None = None
    ) -> list[MasterValue]:
        query = select(MasterValue).where(MasterValue.is_deleted == False)

        if key_id is not None:
            query = query.where(MasterValue.key_id == key_id)

        if hasattr(MasterValue, sort_by):
            col = getattr(MasterValue, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_values(self, key_id: int | None = None) -> int:
        query = select(func.count()).select_from(MasterValue).where(MasterValue.is_deleted == False)
        if key_id is not None:
            query = query.where(MasterValue.key_id == key_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update_value(self, value_id: int, **kwargs) -> MasterValue | None:
        val = await self.get_value(value_id)
        if val:
            # Handle append/remove logic
            append_val = kwargs.pop('append_value', None)
            remove_val = kwargs.pop('remove_value', None)
            
            current_list = list(val.value) if val.value else []
            
            if append_val and append_val not in current_list:
                current_list.append(append_val)
                val.value = current_list
                
            if remove_val and remove_val in current_list:
                current_list.remove(remove_val)
                val.value = current_list

            # Handle other fields
            for k, v in kwargs.items():
                if v is not None and hasattr(val, k):
                    setattr(val, k, v)
            
            await self.session.commit()
            await self.session.refresh(val)
        return val

    async def delete_value(self, value_id: int) -> bool:
        # Soft delete
        val = await self.get_value(value_id)
        if val:
            val.is_deleted = True
            await self.session.commit()
            return True
        return False
