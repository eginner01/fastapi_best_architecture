"""流程实例表模型"""

from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Instance(Base):
    """流程实例表"""

    __tablename__ = 'approval_instance'

    id: Mapped[id_key] = mapped_column(init=False)
    instance_no: Mapped[str] = mapped_column(sa.String(50), unique=True, index=True, default='', comment='流程实例编号')
    flow_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='关联流程定义ID')
    flow_version: Mapped[int] = mapped_column(default=1, comment='使用的流程版本号')
    applicant_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='申请人用户ID')
    title: Mapped[str] = mapped_column(sa.String(255), default='', comment='审批标题')
    status: Mapped[str] = mapped_column(
        sa.String(20),
        default='PENDING',
        index=True,
        comment='实例状态：PENDING(待审批)、APPROVED(已通过)、REJECTED(已驳回)、CANCELLED(已取消)、WITHDRAWN(已撤回)',
    )
    current_node_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='当前所处节点ID')
    business_key: Mapped[str | None] = mapped_column(
        sa.String(100), default=None, index=True, comment='关联业务数据的唯一键'
    )
    business_type: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='业务类型')
    form_data: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='表单数据')
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), default=None, comment='流程开始时间')
    ended_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, comment='流程结束时间'
    )
    duration: Mapped[int | None] = mapped_column(default=None, comment='流程耗时(秒)')
    urgency: Mapped[str] = mapped_column(
        sa.String(20), default='NORMAL', comment='紧急程度：LOW(低)、NORMAL(普通)、HIGH(高)、URGENT(紧急)'
    )
    tags: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='标签')
    attachments: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='附件信息')
    settings: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='实例配置')
