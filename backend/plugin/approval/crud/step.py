"""流程步骤CRUD操作"""

from sqlalchemy import Select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import PageData, paging_data
from backend.plugin.approval.model.opinion import Opinion
from backend.plugin.approval.model.step import Step


class StepDao:
    """流程步骤数据访问对象"""

    @staticmethod
    async def get_by_id(db: AsyncSession, step_id: int) -> Step | None:
        """根据ID获取流程步骤"""
        return await db.get(Step, step_id)

    @staticmethod
    async def get_by_instance(db: AsyncSession, instance_id: int) -> list[Step]:
        """获取流程实例的所有步骤"""
        result = await db.execute(Select(Step).where(Step.instance_id == instance_id).order_by(Step.created_time))
        return list(result.scalars().all())

    @staticmethod
    async def get_pending_by_assignee(
        db: AsyncSession,
        assignee_id: int,
    ) -> PageData[Step]:
        """获取指定用户的待办任务"""
        stmt = (
            Select(Step)
            .where(and_(Step.assignee_id == assignee_id, Step.status == 'PENDING'))
            .order_by(Step.created_time.desc())
        )
        return await paging_data(db, stmt)

    @staticmethod
    async def get_done_by_assignee(
        db: AsyncSession,
        assignee_id: int,
    ) -> PageData[Step]:
        """获取指定用户的已办任务"""
        stmt = (
            Select(Step)
            .where(and_(Step.assignee_id == assignee_id, Step.status.in_(['APPROVED', 'REJECTED', 'DELEGATED'])))
            .order_by(Step.completed_at.desc())
        )
        return await paging_data(db, stmt)

    @staticmethod
    async def get_pending_by_instance_node(db: AsyncSession, instance_id: int, node_id: int) -> list[Step]:
        """获取流程实例在指定节点的待办步骤"""
        result = await db.execute(
            Select(Step).where(
                and_(
                    Step.instance_id == instance_id,
                    Step.node_id == node_id,
                    Step.status == 'PENDING',
                )
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, step: Step) -> Step:
        """创建流程步骤"""
        db.add(step)
        await db.flush()
        return step

    @staticmethod
    async def create_batch(db: AsyncSession, steps: list[Step]) -> list[Step]:
        """批量创建流程步骤"""
        db.add_all(steps)
        await db.flush()
        return steps

    @staticmethod
    async def update(db: AsyncSession, step_id: int, **kwargs) -> int:
        """更新流程步骤"""
        step = await db.get(Step, step_id)
        if not step:
            return 0
        for key, value in kwargs.items():
            if hasattr(step, key) and value is not None:
                setattr(step, key, value)
        await db.flush()
        return 1

    @staticmethod
    async def create_opinion(db: AsyncSession, opinion: Opinion) -> Opinion:
        """创建审批意见"""
        db.add(opinion)
        await db.flush()
        return opinion

    @staticmethod
    async def get_opinions_by_step(db: AsyncSession, step_id: int) -> list[Opinion]:
        """获取步骤的所有意见"""
        result = await db.execute(Select(Opinion).where(Opinion.step_id == step_id).order_by(Opinion.created_time))
        return list(result.scalars().all())


# 创建全局实例
step_dao = StepDao()
