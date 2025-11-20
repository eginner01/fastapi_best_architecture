"""流程实例相关Schema"""

from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


# ==================== 创建流程实例Schema ====================
class CreateInstanceParam(SchemaBase):
    """创建流程实例参数"""

    flow_id: int = Field(..., description='流程定义ID')
    title: str = Field(..., description='实例标题', max_length=255)
    business_key: str | None = Field(default=None, description='业务关联键', max_length=100)
    business_type: str | None = Field(default=None, description='业务类型', max_length=50)
    form_data: dict = Field(..., description='表单数据')
    urgency: str = Field(default='NORMAL', description='紧急程度')
    tags: list[str] | None = Field(default=None, description='标签')
    attachments: list[dict] | None = Field(default=None, description='附件')


# ==================== 处理流程实例Schema ====================
class ProcessInstanceParam(SchemaBase):
    """处理流程实例参数"""

    action: str = Field(..., description='操作：APPROVE/REJECT/DELEGATE/RETURN')
    opinion: str | None = Field(default=None, description='审批意见')
    attachments: list[dict] | None = Field(default=None, description='附件')
    delegate_to: int | None = Field(default=None, description='转交给用户ID')
    return_to_node: int | None = Field(default=None, description='退回到节点ID')


# ==================== 流程实例查询Schema ====================
class InstanceQuery(SchemaBase):
    """流程实例查询参数"""

    flow_id: int | None = Field(default=None, description='流程ID')
    applicant_id: int | None = Field(default=None, description='申请人ID')
    status: str | None = Field(default=None, description='实例状态')
    urgency: str | None = Field(default=None, description='紧急程度')
    business_type: str | None = Field(default=None, description='业务类型')
    title: str | None = Field(default=None, description='标题（模糊查询）')
    start_date: datetime | None = Field(default=None, description='开始日期')
    end_date: datetime | None = Field(default=None, description='结束日期')


# ==================== 流程实例列表详情Schema ====================
class GetInstanceListDetails(SchemaBase):
    """流程实例列表详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    instance_no: str
    flow_id: int
    flow_version: int
    applicant_id: int
    title: str
    status: str
    current_node_id: int | None = None
    business_key: str | None = None
    business_type: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration: int | None = None
    urgency: str
    created_time: datetime


# ==================== 流程步骤详情Schema ====================
class StepDetail(SchemaBase):
    """流程步骤详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    step_no: str
    assignee_id: int
    assignee_name: str | None = None
    status: str
    action: str | None = None
    opinion: str | None = None
    attachments: Any | None = None
    started_at: datetime
    completed_at: datetime | None = None
    duration: int | None = None
    is_read: bool


# ==================== 流程实例详情Schema ====================
class GetInstanceDetails(SchemaBase):
    """流程实例详细信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    instance_no: str
    flow_id: int
    flow_version: int
    applicant_id: int
    title: str
    status: str
    current_node_id: int | None = None
    business_key: str | None = None
    business_type: str | None = None
    form_data: Any | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration: int | None = None
    urgency: str
    tags: Any | None = None
    attachments: Any | None = None
    created_time: datetime
    updated_time: datetime | None = None
    steps: list[StepDetail] = []


# ==================== 待办任务Schema ====================
class TodoTaskSchema(SchemaBase):
    """待办任务"""

    model_config = ConfigDict(from_attributes=True)

    step_id: int
    instance_id: int
    instance_no: str
    title: str
    flow_name: str
    applicant_name: str
    status: str
    urgency: str
    started_at: datetime
    is_read: bool


# ==================== 已办任务Schema ====================
class DoneTaskSchema(SchemaBase):
    """已办任务"""

    model_config = ConfigDict(from_attributes=True)

    step_id: int
    instance_id: int
    instance_no: str
    title: str
    flow_name: str
    applicant_name: str
    action: str
    opinion: str | None = None
    completed_at: datetime
