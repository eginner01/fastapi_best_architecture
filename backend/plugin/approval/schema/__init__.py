"""审批流Schema数据传输对象"""

from backend.plugin.approval.schema.flow import (
    CreateFlowParam,
    FlowQuery,
    GetFlowListDetails,
    UpdateFlowParam,
)
from backend.plugin.approval.schema.instance import (
    CreateInstanceParam,
    GetInstanceListDetails,
    InstanceQuery,
    ProcessInstanceParam,
)

__all__ = [
    'CreateFlowParam',
    'UpdateFlowParam',
    'FlowQuery',
    'GetFlowListDetails',
    'CreateInstanceParam',
    'ProcessInstanceParam',
    'InstanceQuery',
    'GetInstanceListDetails',
]
