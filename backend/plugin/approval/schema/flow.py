"""流程相关Schema"""

from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


# ==================== 流程节点Schema ====================
class FlowNodeSchema(SchemaBase):
    """流程节点Schema"""

    node_no: str = Field(..., description='节点编号')
    name: str = Field(..., description='节点名称')
    node_type: str = Field(default='APPROVAL', description='节点类型')
    approval_type: str | None = Field(default='SINGLE', description='审批类型')
    assignee_type: str | None = Field(default='ROLE', description='审批人类型')
    assignee_value: str | None = Field(default=None, description='审批人值')
    form_permissions: dict | None = Field(default=None, description='表单权限')
    operation_permissions: dict | None = Field(default=None, description='操作权限')
    position_x: float | None = Field(default=0, description='X坐标')
    position_y: float | None = Field(default=0, description='Y坐标')
    order_num: int = Field(default=0, description='顺序号')
    is_first: bool = Field(default=False, description='是否起始节点')
    is_final: bool = Field(default=False, description='是否结束节点')
    settings: dict | None = Field(default=None, description='节点配置')


# ==================== 流程线Schema ====================
class FlowLineSchema(SchemaBase):
    """流程线Schema"""

    line_no: str = Field(..., description='流程线编号')
    from_node_id: str = Field(..., description='起始节点编号')
    to_node_id: str = Field(..., description='目标节点编号')
    condition_type: str | None = Field(default='NONE', description='条件类型')
    condition_expression: str | None = Field(default=None, description='条件表达式')
    priority: int = Field(default=0, description='优先级')
    label: str | None = Field(default=None, description='连线标签')
    settings: dict | None = Field(default=None, description='连线配置')


# ==================== 流程创建Schema ====================
class CreateFlowParam(SchemaBase):
    """创建流程参数"""

    flow_no: str = Field(..., description='流程业务编号', max_length=50)
    name: str = Field(..., description='流程名称', max_length=100)
    description: str | None = Field(default=None, description='流程描述')
    icon: str | None = Field(default=None, description='流程图标', max_length=100)
    category: str | None = Field(default=None, description='流程分类', max_length=50)
    form_schema: dict | None = Field(default=None, description='表单Schema')
    nodes: list[FlowNodeSchema] = Field(default_factory=list, description='流程节点列表')
    lines: list[FlowLineSchema] = Field(default_factory=list, description='流程线列表')
    settings: dict | None = Field(default=None, description='流程配置')


# ==================== 流程更新Schema ====================
class UpdateFlowParam(SchemaBase):
    """更新流程参数"""

    name: str | None = Field(default=None, description='流程名称', max_length=100)
    description: str | None = Field(default=None, description='流程描述')
    icon: str | None = Field(default=None, description='流程图标', max_length=100)
    category: str | None = Field(default=None, description='流程分类', max_length=50)
    is_active: bool | None = Field(default=None, description='是否激活')
    form_schema: dict | None = Field(default=None, description='表单Schema')
    nodes: list[FlowNodeSchema] | None = Field(default=None, description='流程节点列表')
    lines: list[FlowLineSchema] | None = Field(default=None, description='流程线列表')
    settings: dict | None = Field(default=None, description='流程配置')


# ==================== 流程查询Schema ====================
class FlowQuery(SchemaBase):
    """流程查询参数"""

    name: str | None = Field(default=None, description='流程名称（模糊查询）')
    category: str | None = Field(default=None, description='流程分类')
    is_active: bool | None = Field(default=None, description='是否激活')
    is_published: bool | None = Field(default=None, description='是否已发布')


# ==================== 流程列表详情Schema ====================
class GetFlowListDetails(SchemaBase):
    """流程列表详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    flow_no: str
    name: str
    description: str | None = None
    icon: str | None = None
    category: str | None = None
    is_active: bool
    version: int
    is_published: bool
    created_by: int
    created_time: datetime
    updated_time: datetime | None = None


# ==================== 流程详情Schema ====================
class FlowNodeDetail(SchemaBase):
    """流程节点详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    node_no: str
    name: str
    node_type: str
    approval_type: str | None = None
    assignee_type: str | None = None
    assignee_value: str | None = None
    assignee_names: str | None = Field(default=None, description='审批人名称（逗号分隔）')
    form_permissions: Any | None = None
    operation_permissions: Any | None = None
    position_x: float | None = None
    position_y: float | None = None
    order_num: int
    is_first: bool
    is_final: bool
    settings: Any | None = None


class FlowLineDetail(SchemaBase):
    """流程线详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    line_no: str
    from_node_id: int
    to_node_id: int
    condition_type: str | None = None
    condition_expression: str | None = None
    priority: int
    label: str | None = None
    settings: Any | None = None


class GetFlowDetails(SchemaBase):
    """流程详细信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    flow_no: str
    name: str
    description: str | None = None
    icon: str | None = None
    category: str | None = None
    is_active: bool
    version: int
    is_published: bool
    form_schema: Any | None = None
    settings: Any | None = None
    created_by: int
    created_time: datetime
    updated_time: datetime | None = None
    nodes: list[FlowNodeDetail] = []
    lines: list[FlowLineDetail] = []
