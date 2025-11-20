"""流程实例服务"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import PageData
from backend.plugin.approval.crud.instance import instance_dao
from backend.plugin.approval.crud.step import step_dao
from backend.plugin.approval.schema.instance import (
    CreateInstanceParam,
    GetInstanceDetails,
    InstanceQuery,
    ProcessInstanceParam,
)
from backend.plugin.approval.service.flow_engine import flow_engine
from backend.utils import timezone


class InstanceService:
    """流程实例服务"""

    async def create_instance(
        self,
        db: AsyncSession,
        param: CreateInstanceParam,
        applicant_id: int,
    ):
        """
        创建流程实例（发起审批）

        :param db: 数据库会话
        :param param: 创建参数
        :param applicant_id: 申请人ID
        :return: 流程实例
        """
        try:
            instance = await flow_engine.start_instance(
                db=db,
                flow_id=param.flow_id,
                applicant_id=applicant_id,
                title=param.title,
                form_data=param.form_data,
                business_key=param.business_key,
                business_type=param.business_type,
                urgency=param.urgency,
                tags=param.tags,
                attachments=param.attachments,
            )
            log.info(f'用户 {applicant_id} 发起审批: {param.title} (ID: {instance.id})')
            return instance
        except Exception as e:
            log.error(f'创建流程实例失败: {e}')
            raise

    async def process_instance(
        self,
        db: AsyncSession,
        step_id: int,
        param: ProcessInstanceParam,
        user_id: int,
    ) -> bool:
        """
        处理流程实例（审批操作）

        :param db: 数据库会话
        :param step_id: 步骤ID
        :param param: 处理参数
        :param user_id: 当前用户ID
        :return: 是否处理成功
        """
        try:
            result = await flow_engine.process_step(
                db=db,
                step_id=step_id,
                user_id=user_id,
                action=param.action,
                opinion=param.opinion,
                attachments=param.attachments,
                delegate_to=param.delegate_to,
                return_to_node=param.return_to_node,
            )
            log.info(f'用户 {user_id} 处理步骤 {step_id}，操作: {param.action}')
            return result
        except Exception as e:
            log.error(f'处理流程实例失败: {e}')
            raise

    async def get_instance(self, db: AsyncSession, instance_id: int) -> GetInstanceDetails:
        """
        获取流程实例详情

        :param db: 数据库会话
        :param instance_id: 实例ID
        :return: 实例详情
        """
        instance = await instance_dao.get_by_id(db, instance_id)
        if not instance:
            raise errors.NotFoundError(msg='流程实例不存在')

        # 获取步骤列表
        steps = await step_dao.get_by_instance(db, instance_id)

        # 构造返回数据
        instance_dict = instance.__dict__.copy()
        instance_dict['steps'] = steps

        return GetInstanceDetails(**instance_dict)

    async def get_instance_list(
        self,
        db: AsyncSession,
        query: InstanceQuery | None = None,
    ) -> PageData:
        """
        获取流程实例列表

        :param db: 数据库会话
        :param query: 查询参数
        :return: 分页数据
        """
        return await instance_dao.get_list(db, query)

    async def get_my_initiated(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> PageData:
        """
        获取我发起的审批列表

        :param db: 数据库会话
        :param user_id: 用户ID
        :return: 分页数据
        """
        return await instance_dao.get_by_applicant(db, user_id)

    async def get_my_todo(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """
        获取我的待办任务

        :param db: 数据库会话
        :param user_id: 用户ID
        :return: 分页数据
        """
        from sqlalchemy import select
        from backend.plugin.approval.model.instance import Instance
        from backend.plugin.approval.model.flow import Flow
        from backend.plugin.approval.model.step import Step
        from backend.app.admin.model import User
        from backend.plugin.approval.schema.instance import TodoTaskSchema
        
        # 查询待办Step，关联Instance、Flow、申请人
        stmt = (
            select(
                Step.id.label('step_id'),
                Step.instance_id,
                Instance.instance_no,
                Instance.title,
                Flow.name.label('flow_name'),
                User.nickname.label('applicant_name'),
                Step.status,
                Instance.urgency,
                Step.started_at,
                Step.is_read,
            )
            .join(Instance, Step.instance_id == Instance.id)
            .join(Flow, Instance.flow_id == Flow.id)
            .join(User, Instance.applicant_id == User.id)
            .where(Step.assignee_id == user_id)
            .where(Step.status == 'PENDING')
            .order_by(Step.created_time.desc())
        )
        
        from backend.common.pagination import paging_data
        page_data = await paging_data(db, stmt)
        
        # 转换为TodoTaskSchema格式
        tasks = []
        for row in page_data['items']:
            tasks.append(TodoTaskSchema(
                step_id=row.step_id,
                instance_id=row.instance_id,
                instance_no=row.instance_no,
                title=row.title,
                flow_name=row.flow_name,
                applicant_name=row.applicant_name or 'Unknown',
                status=row.status,
                urgency=row.urgency,
                started_at=row.started_at,
                is_read=row.is_read,
            ).model_dump())
        
        page_data['items'] = tasks
        return page_data

    async def get_my_done(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """
        获取我的已办任务

        :param db: 数据库会话
        :param user_id: 用户ID
        :return: 分页数据
        """
        from sqlalchemy import select
        from backend.plugin.approval.model.instance import Instance
        from backend.plugin.approval.model.flow import Flow
        from backend.plugin.approval.model.step import Step
        from backend.app.admin.model import User
        from backend.plugin.approval.schema.instance import DoneTaskSchema
        
        # 查询已办Step，关联Instance、Flow、申请人
        stmt = (
            select(
                Step.id.label('step_id'),
                Step.instance_id,
                Instance.instance_no,
                Instance.title,
                Flow.name.label('flow_name'),
                User.nickname.label('applicant_name'),
                Step.action,
                Step.opinion,
                Step.completed_at,
            )
            .join(Instance, Step.instance_id == Instance.id)
            .join(Flow, Instance.flow_id == Flow.id)
            .join(User, Instance.applicant_id == User.id)
            .where(Step.assignee_id == user_id)
            .where(Step.status.in_(['APPROVED', 'REJECTED', 'DELEGATED', 'CANCELLED']))
            .order_by(Step.completed_at.desc())
        )
        
        from backend.common.pagination import paging_data
        page_data = await paging_data(db, stmt)
        
        # 转换为DoneTaskSchema格式
        tasks = []
        for row in page_data['items']:
            tasks.append(DoneTaskSchema(
                step_id=row.step_id,
                instance_id=row.instance_id,
                instance_no=row.instance_no,
                title=row.title,
                flow_name=row.flow_name,
                applicant_name=row.applicant_name or 'Unknown',
                action=row.action or 'UNKNOWN',
                opinion=row.opinion,
                completed_at=row.completed_at,
            ).model_dump())
        
        page_data['items'] = tasks
        return page_data

    async def cancel_instance(
        self,
        db: AsyncSession,
        instance_id: int,
        user_id: int,
    ) -> bool:
        """
        取消流程实例

        :param db: 数据库会话
        :param instance_id: 实例ID
        :param user_id: 用户ID
        :return: 是否成功
        """
        from backend.plugin.approval.model.step import Step
        from sqlalchemy import select, update
        
        instance = await instance_dao.get_by_id(db, instance_id)
        if not instance:
            raise errors.NotFoundError(msg='流程实例不存在')
        if instance.applicant_id != user_id:
            raise errors.ForbiddenError(msg='只有发起人才能取消流程')
        if instance.status not in ['PENDING', 'RUNNING']:
            raise errors.ForbiddenError(msg='只有进行中的流程才能取消')

        # 更新实例状态
        instance.status = 'CANCELLED'
        instance.ended_at = timezone.now()
        
        # 同步更新所有待办步骤状态为CANCELLED（不删除，留痕）
        await db.execute(
            update(Step)
            .where(Step.instance_id == instance_id)
            .where(Step.status == 'PENDING')
            .values(
                status='CANCELLED',
                action='CANCEL',
                completed_at=timezone.now(),
                duration=0,
            )
        )
        
        await db.commit()
        log.info(f'流程实例 {instance_id} 已取消，所有待办任务已同步更新为CANCELLED状态')
        return True

    async def delete_instance(
        self,
        db: AsyncSession,
        instance_id: int,
        user_id: int,
    ) -> bool:
        """
        删除流程实例（仅允许删除非PENDING状态的实例）

        :param db: 数据库会话
        :param instance_id: 实例ID
        :param user_id: 用户ID
        :return: 是否成功
        """
        instance = await instance_dao.get_by_id(db, instance_id)
        if not instance:
            raise errors.NotFoundError(msg='流程实例不存在')
        if instance.applicant_id != user_id:
            raise errors.ForbiddenError(msg='只有发起人才能删除流程')
        if instance.status == 'PENDING':
            raise errors.ForbiddenError(msg='审批中的流程不能删除，请先撤销')

        # 删除实例（会级联删除关联的步骤）
        result = await instance_dao.delete(db, instance_id)
        await db.commit()
        
        log.info(f'流程实例 {instance_id} 已删除 (用户: {user_id})')
        return result > 0


# 创建全局实例
instance_service = InstanceService()
