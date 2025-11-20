"""流程引擎核心逻辑"""

import json
from datetime import datetime

from simpleeval import SimpleEval
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.log import log
from backend.plugin.approval.crud.flow import flow_dao
from backend.plugin.approval.crud.instance import instance_dao
from backend.plugin.approval.crud.step import step_dao
from backend.plugin.approval.model.flow_line import FlowLine
from backend.plugin.approval.model.flow_node import FlowNode
from backend.plugin.approval.model.instance import Instance
from backend.plugin.approval.model.step import Step
from backend.utils.timezone import timezone


class FlowEngine:
    """流程引擎 - 负责流程的驱动和流转"""

    def __init__(self):
        """初始化流程引擎"""
        self.evaluator = SimpleEval()

    async def start_instance(
        self,
        db: AsyncSession,
        flow_id: int,
        applicant_id: int,
        title: str,
        form_data: dict,
        **kwargs,
    ) -> Instance:
        """
        启动流程实例

        :param db: 数据库会话
        :param flow_id: 流程ID
        :param applicant_id: 申请人ID
        :param title: 实例标题
        :param form_data: 表单数据
        :param kwargs: 其他参数
        :return: 流程实例
        """
        # 获取流程定义
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')
        if not flow.is_active:
            raise errors.ForbiddenError(msg='流程未激活，无法发起')

        # 获取起始节点
        nodes = await flow_dao.get_nodes_by_flow(db, flow_id)
        start_node = next((node for node in nodes if node.is_first), None)
        if not start_node:
            raise errors.ServerError(msg='流程配置错误：缺少起始节点')

        # 生成实例编号
        instance_no = f'INST_{datetime.now().strftime("%Y%m%d%H%M%S")}'

        # 创建流程实例
        instance = Instance(
            instance_no=instance_no,
            flow_id=flow_id,
            flow_version=flow.version,
            applicant_id=applicant_id,
            title=title,
            status='PENDING',
            form_data=form_data,
            started_at=timezone.now(),
            business_key=kwargs.get('business_key'),
            business_type=kwargs.get('business_type'),
            urgency=kwargs.get('urgency', 'NORMAL'),
            tags=kwargs.get('tags'),
            attachments=kwargs.get('attachments'),
        )
        instance = await instance_dao.create(db, instance)

        # 流转到第一个审批节点
        await self._move_to_next_node(db, instance, start_node)

        await db.commit()
        return instance

    async def process_step(
        self,
        db: AsyncSession,
        step_id: int,
        user_id: int,
        action: str,
        opinion: str | None = None,
        **kwargs,
    ) -> bool:
        """
        处理审批步骤

        :param db: 数据库会话
        :param step_id: 步骤ID
        :param user_id: 当前用户ID
        :param action: 操作：APPROVE/REJECT/DELEGATE/RETURN
        :param opinion: 审批意见
        :param kwargs: 其他参数
        :return: 是否处理成功
        """
        # 获取步骤
        step = await step_dao.get_by_id(db, step_id)
        if not step:
            raise errors.NotFoundError(msg='步骤不存在')
        if step.assignee_id != user_id:
            raise errors.ForbiddenError(msg='无权处理此步骤')
        if step.status == 'CANCELLED':
            raise errors.ForbiddenError(msg='该审批已被撤销，无法处理')
        if step.status != 'PENDING':
            raise errors.ForbiddenError(msg='步骤已处理，无法重复操作')

        # 获取实例
        instance = await instance_dao.get_by_id(db, step.instance_id)
        if not instance:
            raise errors.NotFoundError(msg='流程实例不存在')
        if instance.status != 'PENDING':
            raise errors.ForbiddenError(msg='流程实例已结束，无法操作')

        # 更新步骤状态
        now = timezone.now()
        # 确保两个datetime都是带时区的，如果started_at没有时区，添加时区信息
        if step.started_at.tzinfo is None:
            # naive datetime，需要添加时区
            started_at = step.started_at.replace(tzinfo=timezone.tz_info)
        else:
            started_at = step.started_at
        duration = int((now - started_at).total_seconds())
        await step_dao.update(
            db,
            step_id,
            status='APPROVED' if action == 'APPROVE' else 'REJECTED',
            action=action,
            opinion=opinion,
            completed_at=now,
            duration=duration,
            attachments=kwargs.get('attachments'),
        )

        # 处理不同操作
        if action == 'APPROVE':
            await self._handle_approve(db, instance, step)
        elif action == 'REJECT':
            await self._handle_reject(db, instance, step)
        elif action == 'DELEGATE':
            await self._handle_delegate(db, step, kwargs.get('delegate_to'))
        elif action == 'RETURN':
            await self._handle_return(db, instance, step, kwargs.get('return_to_node'))

        await db.commit()
        return True

    async def _move_to_next_node(
        self,
        db: AsyncSession,
        instance: Instance,
        current_node: FlowNode,
    ) -> None:
        """
        移动到下一个节点

        :param db: 数据库会话
        :param instance: 流程实例
        :param current_node: 当前节点
        """
        # 获取从当前节点出发的所有流程线
        lines = await flow_dao.get_lines_from_node(db, current_node.id)
        if not lines:
            # 没有后续节点，流程结束
            await self._complete_instance(db, instance, 'APPROVED')
            return

        # 找到匹配的流程线
        next_line = await self._find_matching_line(instance, lines)
        if not next_line:
            log.warning(f'流程实例 {instance.id} 在节点 {current_node.id} 没有匹配的流程线')
            return

        # 获取下一个节点
        next_node = await flow_dao.get_node_by_id(db, next_line.to_node_id)
        if not next_node:
            raise errors.ServerError(msg=f'节点 {next_line.to_node_id} 不存在')

        # 更新实例当前节点
        await instance_dao.update(db, instance.id, current_node_id=next_node.id)

        # 处理不同类型的节点
        if next_node.node_type == 'END':
            # 结束节点
            await self._complete_instance(db, instance, 'APPROVED')
        elif next_node.node_type == 'APPROVAL':
            # 审批节点，创建待办任务
            await self._create_approval_tasks(db, instance, next_node)
        elif next_node.node_type == 'CC':
            # 抄送节点，创建抄送记录
            await self._create_cc_tasks(db, instance, next_node)
            # 抄送后继续流转
            await self._move_to_next_node(db, instance, next_node)
        elif next_node.node_type == 'CONDITION':
            # 条件节点，直接流转到下一个
            await self._move_to_next_node(db, instance, next_node)

    async def _find_matching_line(self, instance: Instance, lines: list[FlowLine]) -> FlowLine | None:
        """
        找到匹配条件的流程线

        :param instance: 流程实例
        :param lines: 流程线列表
        :return: 匹配的流程线
        """
        for line in lines:
            if line.condition_type == 'NONE':
                return line
            elif line.condition_type == 'EXPRESSION' and line.condition_expression:
                # 使用表达式求值
                try:
                    form_data = instance.form_data or {}
                    self.evaluator.names = form_data
                    result = self.evaluator.eval(line.condition_expression)
                    if result:
                        return line
                except Exception as e:
                    log.error(f'表达式求值失败: {line.condition_expression}, 错误: {e}')

        # 没有匹配的线，返回第一条作为默认
        return lines[0] if lines else None

    async def _create_approval_tasks(
        self,
        db: AsyncSession,
        instance: Instance,
        node: FlowNode,
    ) -> None:
        """
        创建审批任务

        :param db: 数据库会话
        :param instance: 流程实例
        :param node: 审批节点
        """
        # 获取审批人列表
        assignees = await self._get_node_assignees(db, node, instance)
        if not assignees:
            log.warning(f'节点 {node.id} 没有指定审批人')
            return

        # 创建待办步骤
        steps = []
        for idx, assignee_id in enumerate(assignees):
            step_no = f'STEP_{instance.id}_{node.id}_{idx + 1}'
            step = Step(
                instance_id=instance.id,
                node_id=node.id,
                step_no=step_no,
                assignee_id=assignee_id,
                status='PENDING',
                started_at=timezone.now(),
            )
            steps.append(step)

        await step_dao.create_batch(db, steps)

    async def _create_cc_tasks(
        self,
        db: AsyncSession,
        instance: Instance,
        node: FlowNode,
    ) -> None:
        """
        创建抄送任务

        :param db: 数据库会话
        :param instance: 流程实例
        :param node: 抄送节点
        """
        # 抄送节点的实现与审批任务类似，但状态不同
        assignees = await self._get_node_assignees(db, node, instance)
        if not assignees:
            return

        steps = []
        for idx, assignee_id in enumerate(assignees):
            step_no = f'CC_{instance.id}_{node.id}_{idx + 1}'
            step = Step(
                instance_id=instance.id,
                node_id=node.id,
                step_no=step_no,
                assignee_id=assignee_id,
                status='APPROVED',  # 抄送直接标记为完成
                action='CC',
                started_at=timezone.now(),
                completed_at=timezone.now(),
                duration=0,
            )
            steps.append(step)

        await step_dao.create_batch(db, steps)

    async def _get_node_assignees(
        self,
        db: AsyncSession,
        node: FlowNode,
        instance: Instance,
    ) -> list[int]:
        """
        获取节点的审批人列表

        :param db: 数据库会话
        :param node: 节点
        :param instance: 流程实例
        :return: 审批人ID列表
        """
        if not node.assignee_value:
            return []

        assignees = []
        try:
            # 解析审批人配置，支持逗号分隔的字符串（如"1,2,3"）
            assignee_value = node.assignee_value
            if isinstance(assignee_value, str):
                # 尝试解析为JSON
                try:
                    assignee_data = json.loads(assignee_value)
                except json.JSONDecodeError:
                    # 如果不是JSON，按逗号分隔
                    assignee_data = [x.strip() for x in assignee_value.split(',') if x.strip()]
            else:
                assignee_data = assignee_value

            # 确保是列表
            if not isinstance(assignee_data, list):
                assignee_data = [assignee_data]

            if node.assignee_type == 'USER':
                # 指定用户 - 直接使用用户ID列表
                assignees = [int(a) for a in assignee_data]
                log.info(f'节点 {node.id} 审批人（用户）: {assignees}')
                
            elif node.assignee_type == 'ROLE':
                # 指定角色 - 查询角色对应的用户
                from sqlalchemy import select
                from backend.app.admin.model import User
                role_ids = [int(r) for r in assignee_data]
                log.info(f'节点 {node.id} 审批角色: {role_ids}')
                
                # 查询拥有这些角色的用户
                stmt = select(User.id).where(
                    User.roles.any(lambda role: role.id.in_(role_ids))
                )
                result = await db.execute(stmt)
                assignees = [row[0] for row in result.all()]
                log.info(f'节点 {node.id} 审批人（角色映射）: {assignees}')
                
            elif node.assignee_type == 'DEPT':
                # 指定部门 - 查询部门对应的用户
                from sqlalchemy import select
                from backend.app.admin.model import User
                dept_ids = [int(d) for d in assignee_data]
                log.info(f'节点 {node.id} 审批部门: {dept_ids}')
                
                # 查询属于这些部门的用户
                stmt = select(User.id).where(User.dept_id.in_(dept_ids))
                result = await db.execute(stmt)
                assignees = [row[0] for row in result.all()]
                log.info(f'节点 {node.id} 审批人（部门映射）: {assignees}')
                
            elif node.assignee_type == 'INITIATOR':
                # 发起人自己
                assignees = [instance.applicant_id]
                log.info(f'节点 {node.id} 审批人（发起人）: {assignees}')

        except Exception as e:
            log.error(f'解析审批人配置失败: node_id={node.id}, assignee_value={node.assignee_value}, 错误: {e}')

        return assignees

    async def _handle_approve(
        self,
        db: AsyncSession,
        instance: Instance,
        step: Step,
    ) -> None:
        """
        处理同意操作

        :param db: 数据库会话
        :param instance: 流程实例
        :param step: 当前步骤
        """
        # 获取当前节点
        node = await flow_dao.get_node_by_id(db, step.node_id)
        if not node:
            return

        # 检查该节点的所有步骤是否都已完成
        if node.approval_type == 'AND':
            # 会签：需要所有人同意
            all_steps = await step_dao.get_pending_by_instance_node(db, instance.id, node.id)
            if len(all_steps) > 0:
                # 还有待办步骤，不流转
                return
        elif node.approval_type == 'OR':
            # 或签：任意一人同意即可
            # 取消其他待办步骤
            all_steps = await step_dao.get_pending_by_instance_node(db, instance.id, node.id)
            for s in all_steps:
                await step_dao.update(db, s.id, status='CANCELLED')

        # 流转到下一个节点
        await self._move_to_next_node(db, instance, node)

    async def _handle_reject(
        self,
        db: AsyncSession,
        instance: Instance,
        step: Step,
    ) -> None:
        """
        处理拒绝操作

        :param db: 数据库会话
        :param instance: 流程实例
        :param step: 当前步骤
        """
        # 拒绝直接结束流程
        await self._complete_instance(db, instance, 'REJECTED')

    async def _handle_delegate(
        self,
        db: AsyncSession,
        step: Step,
        delegate_to: int | None,
    ) -> None:
        """
        处理转交操作

        :param db: 数据库会话
        :param step: 当前步骤
        :param delegate_to: 转交给的用户ID
        """
        if not delegate_to:
            raise errors.BadRequestError(msg='请指定转交对象')

        # 更新步骤状态为已转交
        await step_dao.update(
            db,
            step.id,
            status='DELEGATED',
            action='DELEGATE',
        )

        # 创建新的待办步骤
        new_step = Step(
            instance_id=step.instance_id,
            node_id=step.node_id,
            step_no=f'{step.step_no}_D',
            assignee_id=delegate_to,
            status='PENDING',
            started_at=timezone.now(),
            delegated_from=step.assignee_id,
        )
        await step_dao.create(db, new_step)

    async def _handle_return(
        self,
        db: AsyncSession,
        instance: Instance,
        step: Step,
        return_to_node: int | None,
    ) -> None:
        """
        处理退回操作

        :param db: 数据库会话
        :param instance: 流程实例
        :param step: 当前步骤
        :param return_to_node: 退回到的节点ID
        """
        if not return_to_node:
            raise errors.BadRequestError(msg='请指定退回节点')

        # 获取退回节点
        node = await flow_dao.get_node_by_id(db, return_to_node)
        if not node:
            raise errors.NotFoundError(msg='退回节点不存在')

        # 更新实例当前节点
        await instance_dao.update(db, instance.id, current_node_id=node.id)

        # 创建新的待办任务
        await self._create_approval_tasks(db, instance, node)

    async def _complete_instance(
        self,
        db: AsyncSession,
        instance: Instance,
        status: str,
    ) -> None:
        """
        完成流程实例

        :param db: 数据库会话
        :param instance: 流程实例
        :param status: 最终状态
        """
        # 更新实例状态
        now = timezone.now()
        # 确保时区一致
        if instance.started_at.tzinfo is None:
            started_at = instance.started_at.replace(tzinfo=timezone.tz_info)
        else:
            started_at = instance.started_at
        duration = int((now - started_at).total_seconds())
        await instance_dao.update(
            db,
            instance.id,
            status=status,
            ended_at=now,
            duration=duration,
        )


# 创建全局实例
flow_engine = FlowEngine()
