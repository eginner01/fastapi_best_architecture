"""流程实例CRUD操作"""

from sqlalchemy import Select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import PageData, paging_data
from backend.plugin.approval.model.instance import Instance
from backend.plugin.approval.schema.instance import InstanceQuery


class InstanceDao:
    """流程实例数据访问对象"""

    @staticmethod
    async def get_by_id(db: AsyncSession, instance_id: int) -> Instance | None:
        """根据ID获取流程实例"""
        return await db.get(Instance, instance_id)

    @staticmethod
    async def get_by_instance_no(db: AsyncSession, instance_no: str) -> Instance | None:
        """根据实例编号获取流程实例"""
        result = await db.execute(Select(Instance).where(Instance.instance_no == instance_no))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: InstanceQuery | None = None,
    ) -> PageData[Instance]:
        """获取流程实例列表（分页）"""
        stmt = Select(Instance).order_by(Instance.created_time.desc())

        if query:
            filters = []
            if query.flow_id:
                filters.append(Instance.flow_id == query.flow_id)
            if query.applicant_id:
                filters.append(Instance.applicant_id == query.applicant_id)
            if query.status:
                filters.append(Instance.status == query.status)
            if query.urgency:
                filters.append(Instance.urgency == query.urgency)
            if query.business_type:
                filters.append(Instance.business_type == query.business_type)
            if query.title:
                filters.append(Instance.title.like(f'%{query.title}%'))
            if query.start_date:
                filters.append(Instance.started_at >= query.start_date)
            if query.end_date:
                filters.append(Instance.started_at <= query.end_date)
            if filters:
                stmt = stmt.where(and_(*filters))

        return await paging_data(db, stmt)

    @staticmethod
    async def get_by_applicant(
        db: AsyncSession,
        applicant_id: int,
    ) -> PageData[Instance]:
        """获取指定用户发起的流程实例列表"""
        stmt = Select(Instance).where(Instance.applicant_id == applicant_id).order_by(Instance.created_time.desc())
        return await paging_data(db, stmt)

    @staticmethod
    async def create(db: AsyncSession, instance: Instance) -> Instance:
        """创建流程实例"""
        db.add(instance)
        await db.flush()
        return instance

    @staticmethod
    async def update(db: AsyncSession, instance_id: int, **kwargs) -> int:
        """更新流程实例"""
        instance = await db.get(Instance, instance_id)
        if not instance:
            return 0
        for key, value in kwargs.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        await db.flush()
        return 1

    @staticmethod
    async def delete(db: AsyncSession, instance_id: int) -> int:
        """删除流程实例"""
        instance = await db.get(Instance, instance_id)
        if not instance:
            return 0
        await db.delete(instance)
        await db.flush()
        return 1


# 创建全局实例
instance_dao = InstanceDao()
