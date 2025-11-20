"""流程CRUD操作"""

from sqlalchemy import Select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import PageData, paging_data
from backend.plugin.approval.model.flow import Flow
from backend.plugin.approval.model.flow_line import FlowLine
from backend.plugin.approval.model.flow_node import FlowNode
from backend.plugin.approval.schema.flow import FlowQuery


class FlowDao:
    """流程数据访问对象"""

    @staticmethod
    async def get_by_id(db: AsyncSession, flow_id: int) -> Flow | None:
        """根据ID获取流程"""
        return await db.get(Flow, flow_id)

    @staticmethod
    async def get_by_flow_no(db: AsyncSession, flow_no: str) -> Flow | None:
        """根据流程编号获取流程"""
        result = await db.execute(Select(Flow).where(Flow.flow_no == flow_no))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: FlowQuery | None = None,
    ) -> PageData[Flow]:
        """获取流程列表（分页）"""
        stmt = Select(Flow).order_by(Flow.created_time.desc())

        if query:
            filters = []
            if query.name:
                filters.append(Flow.name.like(f'%{query.name}%'))
            if query.category:
                filters.append(Flow.category == query.category)
            if query.is_active is not None:
                filters.append(Flow.is_active == query.is_active)
            if query.is_published is not None:
                filters.append(Flow.is_published == query.is_published)
            if filters:
                stmt = stmt.where(and_(*filters))

        return await paging_data(db, stmt)

    @staticmethod
    async def get_all_active(db: AsyncSession) -> list[Flow]:
        """获取所有激活的流程"""
        result = await db.execute(Select(Flow).where(Flow.is_active == True).order_by(Flow.name))  # noqa: E712
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, flow: Flow) -> Flow:
        """创建流程"""
        db.add(flow)
        await db.flush()
        return flow

    @staticmethod
    async def update(db: AsyncSession, flow_id: int, **kwargs) -> int:
        """更新流程"""
        flow = await db.get(Flow, flow_id)
        if not flow:
            return 0
        for key, value in kwargs.items():
            if hasattr(flow, key) and value is not None:
                setattr(flow, key, value)
        await db.flush()
        return 1

    @staticmethod
    async def delete(db: AsyncSession, flow_id: int) -> int:
        """删除流程"""
        flow = await db.get(Flow, flow_id)
        if not flow:
            return 0
        await db.delete(flow)
        await db.flush()
        return 1

    @staticmethod
    async def get_nodes_by_flow(db: AsyncSession, flow_id: int) -> list[FlowNode]:
        """获取流程的所有节点"""
        result = await db.execute(Select(FlowNode).where(FlowNode.flow_id == flow_id).order_by(FlowNode.order_num))
        return list(result.scalars().all())

    @staticmethod
    async def get_node_by_id(db: AsyncSession, node_id: int) -> FlowNode | None:
        """根据ID获取节点"""
        return await db.get(FlowNode, node_id)

    @staticmethod
    async def get_lines_by_flow(db: AsyncSession, flow_id: int) -> list[FlowLine]:
        """获取流程的所有流程线"""
        result = await db.execute(Select(FlowLine).where(FlowLine.flow_id == flow_id).order_by(FlowLine.priority.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_lines_from_node(db: AsyncSession, node_id: int) -> list[FlowLine]:
        """获取从指定节点出发的所有流程线"""
        result = await db.execute(
            Select(FlowLine).where(FlowLine.from_node_id == node_id).order_by(FlowLine.priority.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_node(db: AsyncSession, node: FlowNode) -> FlowNode:
        """创建流程节点"""
        db.add(node)
        await db.flush()
        return node

    @staticmethod
    async def create_line(db: AsyncSession, line: FlowLine) -> FlowLine:
        """创建流程线"""
        db.add(line)
        await db.flush()
        return line

    @staticmethod
    async def delete_nodes_by_flow(db: AsyncSession, flow_id: int) -> int:
        """删除流程的所有节点"""
        nodes = await FlowDao.get_nodes_by_flow(db, flow_id)
        for node in nodes:
            await db.delete(node)
        await db.flush()
        return len(nodes)

    @staticmethod
    async def delete_lines_by_flow(db: AsyncSession, flow_id: int) -> int:
        """删除流程的所有流程线"""
        lines = await FlowDao.get_lines_by_flow(db, flow_id)
        for line in lines:
            await db.delete(line)
        await db.flush()
        return len(lines)


# 创建全局实例
flow_dao = FlowDao()
