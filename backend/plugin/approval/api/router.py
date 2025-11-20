"""审批流路由"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.core.conf import settings
from backend.database.db import CurrentSession
from backend.plugin.approval.schema.flow import (
    CreateFlowParam,
    FlowQuery,
    GetFlowDetails,
    GetFlowListDetails,
    UpdateFlowParam,
)
from backend.plugin.approval.schema.instance import (
    CreateInstanceParam,
    GetInstanceDetails,
    GetInstanceListDetails,
    InstanceQuery,
    ProcessInstanceParam,
)
from backend.plugin.approval.service.flow_service import flow_service
from backend.plugin.approval.service.instance_service import instance_service

# 流程管理路由
flow_router = APIRouter(prefix='/flows', tags=['审批流-流程管理'])

# 流程实例路由
instance_router = APIRouter(prefix='/instances', tags=['审批流-流程实例'])

# 审批步骤路由
step_router = APIRouter(prefix='/steps', tags=['审批流-审批步骤'])

# 我的待办路由
my_router = APIRouter(prefix='/my', tags=['审批流-我的任务'])


@flow_router.post('', summary='创建流程', dependencies=[DependsJwtAuth])
async def create_flow(
    request: Request,
    param: CreateFlowParam,
    db: CurrentSession,
) -> ResponseModel:
    """创建新的审批流程"""
    flow = await flow_service.create_flow(db, param, request.user.id)
    return response_base.success(data=flow)


@flow_router.get('', summary='获取流程列表', dependencies=[DependsJwtAuth, DependsPagination])
async def get_flow_list(
    db: CurrentSession,
    name: str | None = Query(default=None, description='流程名称'),
    category: str | None = Query(default=None, description='流程分类'),
    is_active: bool | None = Query(default=None, description='是否激活'),
    is_published: bool | None = Query(default=None, description='是否已发布'),
) -> ResponseSchemaModel[PageData[GetFlowListDetails]]:
    """获取流程列表（分页）"""
    query = FlowQuery(
        name=name,
        category=category,
        is_active=is_active,
        is_published=is_published,
    )
    data = await flow_service.get_flow_list(db, query)
    return response_base.success(data=data)


@flow_router.get('/{flow_id}', summary='获取流程详情', dependencies=[DependsJwtAuth])
async def get_flow(
    flow_id: int,
    db: CurrentSession,
) -> ResponseSchemaModel[GetFlowDetails]:
    """获取流程详细信息"""
    data = await flow_service.get_flow(db, flow_id)
    return response_base.success(data=data)


@flow_router.put('/{flow_id}', summary='更新流程', dependencies=[DependsJwtAuth])
async def update_flow(
    flow_id: int,
    param: UpdateFlowParam,
    db: CurrentSession,
) -> ResponseModel:
    """更新流程信息"""
    result = await flow_service.update_flow(db, flow_id, param)
    return response_base.success(data=result)


@flow_router.delete('/{flow_id}', summary='删除流程', dependencies=[DependsJwtAuth])
async def delete_flow(
    flow_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """删除流程"""
    result = await flow_service.delete_flow(db, flow_id)
    return response_base.success(data=result)


@flow_router.post('/{flow_id}/publish', summary='发布流程', dependencies=[DependsJwtAuth])
async def publish_flow(
    flow_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """发布流程，使其可被用户发起"""
    result = await flow_service.publish_flow(db, flow_id)
    return response_base.success(data=result)


@flow_router.post('/{flow_id}/unpublish', summary='取消发布流程', dependencies=[DependsJwtAuth])
async def unpublish_flow(
    flow_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """取消发布流程"""
    result = await flow_service.unpublish_flow(db, flow_id)
    return response_base.success(data=result)


@instance_router.post('', summary='发起审批', dependencies=[DependsJwtAuth])
async def create_instance(
    request: Request,
    param: CreateInstanceParam,
    db: CurrentSession,
) -> ResponseModel:
    """发起新的审批申请"""
    instance = await instance_service.create_instance(db, param, request.user.id)
    return response_base.success(data=instance)


@instance_router.get('', summary='获取流程实例列表', dependencies=[DependsJwtAuth, DependsPagination])
async def get_instance_list(
    db: CurrentSession,
    flow_id: int | None = Query(default=None, description='流程ID'),
    applicant_id: int | None = Query(default=None, description='申请人ID'),
    status: str | None = Query(default=None, description='实例状态'),
    urgency: str | None = Query(default=None, description='紧急程度'),
    business_type: str | None = Query(default=None, description='业务类型'),
    title: str | None = Query(default=None, description='标题'),
) -> ResponseSchemaModel[PageData[GetInstanceListDetails]]:
    """获取流程实例列表（分页）"""
    query = InstanceQuery(
        flow_id=flow_id,
        applicant_id=applicant_id,
        status=status,
        urgency=urgency,
        business_type=business_type,
        title=title,
    )
    data = await instance_service.get_instance_list(db, query)
    return response_base.success(data=data)


@instance_router.get('/{instance_id}', summary='获取流程实例详情', dependencies=[DependsJwtAuth])
async def get_instance(
    instance_id: int,
    db: CurrentSession,
) -> ResponseSchemaModel[GetInstanceDetails]:
    data = await instance_service.get_instance(db, instance_id)
    return response_base.success(data=data)


@instance_router.post('/{step_id}/process', summary='处理审批', dependencies=[DependsJwtAuth])
async def process_instance(
    request: Request,
    step_id: int,
    param: ProcessInstanceParam,
    db: CurrentSession,
) -> ResponseModel:
    """处理审批任务（同意/拒绝/转交/退回）"""
    result = await instance_service.process_instance(db, step_id, param, request.user.id)
    return response_base.success(data=result)


@step_router.post('/{step_id}/process', summary='处理审批步骤', dependencies=[DependsJwtAuth])
async def process_step(
    request: Request,
    step_id: int,
    param: ProcessInstanceParam,
    db: CurrentSession,
) -> ResponseModel:
    """处理审批步骤（同意/拒绝/转交/退回）"""
    result = await instance_service.process_instance(db, step_id, param, request.user.id)
    return response_base.success(data=result)


@instance_router.post('/{instance_id}/cancel', summary='取消审批', dependencies=[DependsJwtAuth])
async def cancel_instance(
    request: Request,
    instance_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """取消审批实例"""
    result = await instance_service.cancel_instance(db, instance_id, request.user.id)
    return response_base.success(data=result)


@instance_router.delete('/{instance_id}', summary='删除审批实例', dependencies=[DependsJwtAuth])
async def delete_instance(
    request: Request,
    instance_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """删除审批实例（仅允许删除非审批中的实例）"""
    result = await instance_service.delete_instance(db, instance_id, request.user.id)
    return response_base.success(data=result)


@my_router.get('/initiated', summary='我发起的', dependencies=[DependsJwtAuth, DependsPagination])
async def get_my_initiated(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetInstanceListDetails]]:
    data = await instance_service.get_my_initiated(db, request.user.id)
    return response_base.success(data=data)


@my_router.get('/todo', summary='我的待办', dependencies=[DependsJwtAuth, DependsPagination])
async def get_my_todo(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    data = await instance_service.get_my_todo(db, request.user.id)
    return response_base.success(data=data)


@my_router.get('/done', summary='我的已办', dependencies=[DependsJwtAuth, DependsPagination])
async def get_my_done(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    data = await instance_service.get_my_done(db, request.user.id)
    return response_base.success(data=data)


# 合并所有路由到 v1
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/approval', tags=['审批流'])
v1.include_router(flow_router)
v1.include_router(instance_router)
v1.include_router(step_router)
v1.include_router(my_router)
