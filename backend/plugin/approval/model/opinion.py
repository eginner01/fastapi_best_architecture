"""审批意见表模型"""

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Opinion(Base):
    """审批意见表 - 记录详细的审批意见和评论"""

    __tablename__ = 'approval_opinion'

    id: Mapped[id_key] = mapped_column(init=False)
    step_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='关联流程步骤ID')
    author_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='意见作者用户ID')
    author_name: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='作者姓名（冗余字段）')
    opinion_type: Mapped[str] = mapped_column(
        sa.String(20), default='COMMENT', comment='意见类型：COMMENT(评论)、APPROVE(同意意见)、REJECT(拒绝意见)'
    )
    content: Mapped[str] = mapped_column(sa.Text, default='', comment='意见内容')
    attachments: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='附件信息（JSON数组）')
    is_private: Mapped[bool] = mapped_column(default=False, comment='是否为私密意见（仅管理员可见）')
    reply_to: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='回复的意见ID')
