"""流程步骤表模型"""

from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Step(Base):
    """流程步骤表 - 记录流程实例在每个节点的处理情况"""

    __tablename__ = 'approval_step'

    id: Mapped[id_key] = mapped_column(init=False)
    instance_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='所属流程实例ID')
    node_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='关联流程节点ID')
    step_no: Mapped[str] = mapped_column(sa.String(50), default='', comment='步骤编号')
    assignee_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='指定审批人用户ID')
    assignee_name: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='审批人姓名（冗余字段）')
    status: Mapped[str] = mapped_column(
        sa.String(20),
        default='PENDING',
        index=True,
        comment='步骤状态：PENDING(待处理)、APPROVED(已同意)、REJECTED(已拒绝)、DELEGATED(已转交)、WITHDRAWN(已撤回)、CANCELLED(已取消)',
    )
    action: Mapped[str | None] = mapped_column(
        sa.String(20), default=None, comment='执行操作：APPROVE(同意)、REJECT(拒绝)、DELEGATE(转交)、RETURN(退回)'
    )
    opinion: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='审批意见')
    attachments: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='附件信息（JSON数组）')
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), default=None, comment='步骤开始时间')
    completed_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, comment='步骤完成时间'
    )
    duration: Mapped[int | None] = mapped_column(default=None, comment='处理耗时（秒）')
    is_read: Mapped[bool] = mapped_column(default=False, comment='是否已读')
    delegated_from: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='转交来源用户ID')
    settings: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='步骤配置（JSON格式）')
