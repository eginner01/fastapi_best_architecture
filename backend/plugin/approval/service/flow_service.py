"""流程管理服务"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import PageData
from backend.plugin.approval.crud.flow import flow_dao
from backend.plugin.approval.model.flow import Flow
from backend.plugin.approval.model.flow_line import FlowLine
from backend.plugin.approval.model.flow_node import FlowNode
from backend.plugin.approval.schema.flow import (
    CreateFlowParam,
    FlowQuery,
    GetFlowDetails,
    UpdateFlowParam,
)


class FlowService:
    """流程管理服务"""

    async def create_flow(
        self,
        db: AsyncSession,
        param: CreateFlowParam,
        created_by: int,
    ) -> Flow:
        """
        创建流程

        :param db: 数据库会话
        :param param: 创建参数
        :param created_by: 创建者ID
        :return: 流程对象
        """
        # 检查流程编号是否已存在
        existing = await flow_dao.get_by_flow_no(db, param.flow_no)
        if existing:
            raise errors.BadRequestError(msg=f'流程编号 {param.flow_no} 已存在')

        # 创建流程
        flow = Flow(
            flow_no=param.flow_no,
            name=param.name,
            description=param.description,
            icon=param.icon,
            category=param.category,
            form_schema=param.form_schema,
            settings=param.settings,
            created_by=created_by,
        )
        flow = await flow_dao.create(db, flow)

        # 创建节点
        node_mapping = {}  # node_no -> node_id 映射
        for node_param in param.nodes:
            node = FlowNode(
                flow_id=flow.id,
                node_no=node_param.node_no,
                name=node_param.name,
                node_type=node_param.node_type,
                approval_type=node_param.approval_type,
                assignee_type=node_param.assignee_type,
                assignee_value=node_param.assignee_value,
                form_permissions=node_param.form_permissions,
                operation_permissions=node_param.operation_permissions,
                position_x=node_param.position_x,
                position_y=node_param.position_y,
                order_num=node_param.order_num,
                is_first=node_param.is_first,
                is_final=node_param.is_final,
                settings=node_param.settings,
            )
            node = await flow_dao.create_node(db, node)
            node_mapping[node_param.node_no] = node.id

        # 创建流程线
        for line_param in param.lines:
            line = FlowLine(
                flow_id=flow.id,
                line_no=line_param.line_no,
                from_node_id=node_mapping.get(line_param.from_node_id, 0),
                to_node_id=node_mapping.get(line_param.to_node_id, 0),
                condition_type=line_param.condition_type,
                condition_expression=line_param.condition_expression,
                priority=line_param.priority,
                label=line_param.label,
                settings=line_param.settings,
            )
            await flow_dao.create_line(db, line)

        await db.commit()
        log.info(f'用户 {created_by} 创建流程: {flow.name} (ID: {flow.id})')
        return flow

    async def update_flow(
        self,
        db: AsyncSession,
        flow_id: int,
        param: UpdateFlowParam,
    ) -> bool:
        """
        更新流程

        :param db: 数据库会话
        :param flow_id: 流程ID
        :param param: 更新参数
        :return: 是否更新成功
        """
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')

        # 更新基本信息
        update_data = param.model_dump(exclude_unset=True, exclude={'nodes', 'lines'})
        if update_data:
            await flow_dao.update(db, flow_id, **update_data)

        # 如果更新了节点和线，需要重新创建
        if param.nodes is not None or param.lines is not None:
            # 删除旧的节点和线
            await flow_dao.delete_nodes_by_flow(db, flow_id)
            await flow_dao.delete_lines_by_flow(db, flow_id)

            # 创建新的节点
            node_mapping = {}
            if param.nodes:
                for node_param in param.nodes:
                    node = FlowNode(
                        flow_id=flow_id,
                        node_no=node_param.node_no,
                        name=node_param.name,
                        node_type=node_param.node_type,
                        approval_type=node_param.approval_type,
                        assignee_type=node_param.assignee_type,
                        assignee_value=node_param.assignee_value,
                        form_permissions=node_param.form_permissions,
                        operation_permissions=node_param.operation_permissions,
                        position_x=node_param.position_x,
                        position_y=node_param.position_y,
                        order_num=node_param.order_num,
                        is_first=node_param.is_first,
                        is_final=node_param.is_final,
                        settings=node_param.settings,
                    )
                    node = await flow_dao.create_node(db, node)
                    node_mapping[node_param.node_no] = node.id

            # 创建新的流程线
            if param.lines:
                for line_param in param.lines:
                    line = FlowLine(
                        flow_id=flow_id,
                        line_no=line_param.line_no,
                        from_node_id=node_mapping.get(line_param.from_node_id, 0),
                        to_node_id=node_mapping.get(line_param.to_node_id, 0),
                        condition_type=line_param.condition_type,
                        condition_expression=line_param.condition_expression,
                        priority=line_param.priority,
                        label=line_param.label,
                        settings=line_param.settings,
                    )
                    await flow_dao.create_line(db, line)

        await db.commit()
        log.info(f'流程 {flow_id} 已更新')
        return True

    async def delete_flow(self, db: AsyncSession, flow_id: int) -> bool:
        """
        删除流程

        :param db: 数据库会话
        :param flow_id: 流程ID
        :return: 是否删除成功
        """
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')

        # 删除关联的节点和线
        await flow_dao.delete_nodes_by_flow(db, flow_id)
        await flow_dao.delete_lines_by_flow(db, flow_id)

        # 删除流程
        await flow_dao.delete(db, flow_id)
        await db.commit()
        log.info(f'流程 {flow_id} 已删除')
        return True

    async def get_flow(self, db: AsyncSession, flow_id: int) -> GetFlowDetails:
        """
        获取流程详情

        :param db: 数据库会话
        :param flow_id: 流程ID
        :return: 流程详情
        """
        from sqlalchemy import select
        from backend.app.admin.model import User, Role, Dept
        
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')

        # 获取节点和线
        nodes = await flow_dao.get_nodes_by_flow(db, flow_id)
        lines = await flow_dao.get_lines_by_flow(db, flow_id)

        # 为每个节点补充审批人名称信息
        from backend.plugin.approval.schema.flow import FlowNodeDetail, FlowLineDetail
        
        enriched_nodes = []
        for node in nodes:
            node_dict = node.__dict__.copy()
            
            # 解析审批人并获取名称
            if node.assignee_value and node.assignee_type:
                try:
                    log.info(f'节点 {node.id} 审批人配置: type={node.assignee_type}, value={node.assignee_value}')
                    
                    # 解析ID列表
                    assignee_ids = []
                    if isinstance(node.assignee_value, str):
                        assignee_ids = [x.strip() for x in node.assignee_value.split(',') if x.strip()]
                    
                    log.info(f'节点 {node.id} 解析出的ID列表: {assignee_ids}')
                    
                    assignee_names = []
                    if node.assignee_type == 'USER':
                        # 查询用户名
                        int_ids = [int(id) for id in assignee_ids]
                        log.info(f'查询用户ID: {int_ids}')
                        
                        stmt = select(User.id, User.nickname, User.username).where(
                            User.id.in_(int_ids)
                        )
                        result = await db.execute(stmt)
                        users = result.all()
                        log.info(f'查询到的用户: {[(u.id, u.nickname, u.username) for u in users]}')
                        
                        assignee_names = [f"{u.nickname or u.username}" for u in users]
                        
                    elif node.assignee_type == 'ROLE':
                        # 查询角色名
                        int_ids = [int(id) for id in assignee_ids]
                        stmt = select(Role.id, Role.name).where(
                            Role.id.in_(int_ids)
                        )
                        result = await db.execute(stmt)
                        roles = result.all()
                        log.info(f'查询到的角色: {[(r.id, r.name) for r in roles]}')
                        assignee_names = [r.name for r in roles]
                        
                    elif node.assignee_type == 'DEPT':
                        # 查询部门名
                        int_ids = [int(id) for id in assignee_ids]
                        stmt = select(Dept.id, Dept.name).where(
                            Dept.id.in_(int_ids)
                        )
                        result = await db.execute(stmt)
                        depts = result.all()
                        log.info(f'查询到的部门: {[(d.id, d.name) for d in depts]}')
                        assignee_names = [d.name for d in depts]
                    
                    # 添加名称字段
                    node_dict['assignee_names'] = ', '.join(assignee_names) if assignee_names else None
                    log.info(f'节点 {node.id} 最终名称: {node_dict["assignee_names"]}')
                    
                except Exception as e:
                    log.error(f'获取节点审批人名称失败: {e}', exc_info=True)
                    node_dict['assignee_names'] = None
            
            # 转换为FlowNodeDetail对象
            enriched_nodes.append(FlowNodeDetail(**node_dict))

        # 转换流程线为FlowLineDetail对象
        line_details = [FlowLineDetail.model_validate(line) for line in lines]

        # 构造返回数据
        flow_dict = flow.__dict__.copy()
        flow_dict['nodes'] = enriched_nodes
        flow_dict['lines'] = line_details

        return GetFlowDetails(**flow_dict)

    async def get_flow_list(
        self,
        db: AsyncSession,
        query: FlowQuery | None = None,
    ) -> PageData:
        """
        获取流程列表

        :param db: 数据库会话
        :param query: 查询参数
        :return: 分页数据
        """
        return await flow_dao.get_list(db, query)

    async def publish_flow(self, db: AsyncSession, flow_id: int) -> bool:
        """
        发布流程

        :param db: 数据库会话
        :param flow_id: 流程ID
        :return: 是否发布成功
        """
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')

        await flow_dao.update(db, flow_id, is_published=True, is_active=True)
        await db.commit()
        log.info(f'流程 {flow_id} 已发布')
        return True

    async def unpublish_flow(self, db: AsyncSession, flow_id: int) -> bool:
        """
        取消发布流程

        :param db: 数据库会话
        :param flow_id: 流程ID
        :return: 是否取消成功
        """
        flow = await flow_dao.get_by_id(db, flow_id)
        if not flow:
            raise errors.NotFoundError(msg='流程不存在')

        await flow_dao.update(db, flow_id, is_published=False)
        await db.commit()
        log.info(f'流程 {flow_id} 已取消发布')
        return True


# 创建全局实例
flow_service = FlowService()
