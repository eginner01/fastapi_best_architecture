"""流程线表模型"""

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class FlowLine(Base):
    """流程线表 - 定义流程节点之间的连接关系和流转条件"""

    __tablename__ = 'approval_flow_line'

    id: Mapped[id_key] = mapped_column(init=False)
    flow_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='所属流程ID')
    line_no: Mapped[str] = mapped_column(sa.String(50), default='', comment='流程线编号，例如 line_001')
    from_node_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='起始节点ID')
    to_node_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='目标节点ID')
    condition_type: Mapped[str | None] = mapped_column(
        sa.String(20), default='NONE', comment='条件类型：NONE(无条件)、APPROVED(通过)、REJECTED(驳回)、EXPRESSION(表达式)'
    )
    condition_expression: Mapped[str | None] = mapped_column(
        sa.String(500), default=None, comment='条件表达式，例如 amount > 1000'
    )
    priority: Mapped[int] = mapped_column(default=0, comment='优先级，当多个条件满足时按优先级选择')
    label: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='连线标签')
    settings: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='连线配置（JSON格式）')
