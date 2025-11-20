"""流程节点表模型"""

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class FlowNode(Base):
    """流程节点表"""

    __tablename__ = 'approval_flow_node'

    id: Mapped[id_key] = mapped_column(init=False)
    flow_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, default=0, comment='所属流程ID')
    node_no: Mapped[str] = mapped_column(sa.String(50), default='', comment='节点编号')
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='节点名称')
    node_type: Mapped[str] = mapped_column(
        sa.String(20),
        default='APPROVAL',
        comment='节点类型：START(开始)、APPROVAL(审批)、CONDITION(条件)、CC(抄送)、END(结束)',
    )
    approval_type: Mapped[str | None] = mapped_column(
        sa.String(20), default='SINGLE', comment='审批类型：SINGLE(单签)、AND(会签)、OR(或签)'
    )
    assignee_type: Mapped[str | None] = mapped_column(
        sa.String(20),
        default='ROLE',
        comment='审批人类型：ROLE(角色)、USER(指定用户)、DEPT(部门)、INITIATOR(发起人自选)、DYNAMIC(动态计算)',
    )
    assignee_value: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='审批人值')
    form_permissions: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='表单权限配置')
    operation_permissions: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='操作权限配置')
    position_x: Mapped[float | None] = mapped_column(sa.Float, default=0, comment='节点X坐标')
    position_y: Mapped[float | None] = mapped_column(sa.Float, default=0, comment='节点Y坐标')
    order_num: Mapped[int] = mapped_column(default=0, comment='节点顺序号')
    is_first: Mapped[bool] = mapped_column(default=False, comment='是否为流程起始节点')
    is_final: Mapped[bool] = mapped_column(default=False, comment='是否为流程结束节点')
    settings: Mapped[str | None] = mapped_column(sa.JSON, default=None, comment='节点配置')
