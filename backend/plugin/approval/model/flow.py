"""流程表模型"""

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Flow(Base):
    """流程表 - 存储审批流程模板定义"""

    __tablename__ = 'approval_flow'

    id: Mapped[id_key] = mapped_column(init=False)
    flow_no: Mapped[str] = mapped_column(
        sa.String(50), unique=True, index=True, default='', comment='流程业务编号，例如 LEAVE_001'
    )
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='流程名称，例如 请假流程')
    description: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='流程详细描述')
    icon: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='流程图标')
    category: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='流程分类')
    is_active: Mapped[bool] = mapped_column(default=True, comment='流程是否激活（只有激活的流程才能被发起）')
    version: Mapped[int] = mapped_column(default=1, comment='流程版本号')
    is_published: Mapped[bool] = mapped_column(default=False, comment='是否已发布')
    form_schema: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='表单JSON Schema定义')
    settings: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='流程配置（JSON格式）')
    created_by: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='创建者用户ID')
