-- ============================================
-- 审批流插件数据库初始化脚本 (PostgreSQL)
-- ============================================
-- 包含内容:
-- 1. 审批流程表 (approval_flow)
-- 2. 流程节点表 (approval_flow_node)
-- 3. 流程线表 (approval_flow_line)
-- 4. 流程实例表 (approval_instance)
-- 5. 流程步骤表 (approval_step) - 包含 node_no 字段
-- 6. 审批意见表 (approval_opinion)
-- 7. 侧边栏菜单 (sys_menu) - 10个菜单项
-- ============================================

-- 流程表
CREATE TABLE IF NOT EXISTS approval_flow (
    id BIGSERIAL PRIMARY KEY,
    flow_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    is_published BOOLEAN DEFAULT FALSE,
    form_schema JSONB,
    settings JSONB,
    created_by BIGINT NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_flow_no ON approval_flow(flow_no);
CREATE INDEX IF NOT EXISTS idx_category ON approval_flow(category);
CREATE INDEX IF NOT EXISTS idx_is_active ON approval_flow(is_active);
COMMENT ON TABLE approval_flow IS '审批流程表';

-- 流程节点表
CREATE TABLE IF NOT EXISTS approval_flow_node (
    id BIGSERIAL PRIMARY KEY,
    flow_id BIGINT NOT NULL,
    node_no VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    node_type VARCHAR(20) DEFAULT 'APPROVAL',
    approval_type VARCHAR(20) DEFAULT 'SINGLE',
    assignee_type VARCHAR(20) DEFAULT 'ROLE',
    assignee_value VARCHAR(500),
    form_permissions JSONB,
    operation_permissions JSONB,
    position_x FLOAT DEFAULT 0,
    position_y FLOAT DEFAULT 0,
    order_num INTEGER DEFAULT 0,
    is_first BOOLEAN DEFAULT FALSE,
    is_final BOOLEAN DEFAULT FALSE,
    settings JSONB,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_flow_id ON approval_flow_node(flow_id);
CREATE INDEX IF NOT EXISTS idx_order_num ON approval_flow_node(order_num);
COMMENT ON TABLE approval_flow_node IS '流程节点表';

-- 流程线表
CREATE TABLE IF NOT EXISTS approval_flow_line (
    id BIGSERIAL PRIMARY KEY,
    flow_id BIGINT NOT NULL,
    line_no VARCHAR(50) NOT NULL,
    from_node_id BIGINT NOT NULL,
    to_node_id BIGINT NOT NULL,
    condition_type VARCHAR(20) DEFAULT 'NONE',
    condition_expression VARCHAR(500),
    priority INTEGER DEFAULT 0,
    label VARCHAR(100),
    settings JSONB,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_flow_line_flow_id ON approval_flow_line(flow_id);
CREATE INDEX IF NOT EXISTS idx_from_node ON approval_flow_line(from_node_id);
CREATE INDEX IF NOT EXISTS idx_priority ON approval_flow_line(priority);
COMMENT ON TABLE approval_flow_line IS '流程线表';

-- 流程实例表
CREATE TABLE IF NOT EXISTS approval_instance (
    id BIGSERIAL PRIMARY KEY,
    instance_no VARCHAR(50) NOT NULL UNIQUE,
    flow_id BIGINT NOT NULL,
    flow_version INTEGER DEFAULT 1,
    applicant_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    current_node_id BIGINT,
    business_key VARCHAR(100),
    business_type VARCHAR(50),
    form_data JSONB,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration INTEGER,
    urgency VARCHAR(20) DEFAULT 'NORMAL',
    tags JSONB,
    attachments JSONB,
    settings JSONB,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_instance_no ON approval_instance(instance_no);
CREATE INDEX IF NOT EXISTS idx_instance_flow_id ON approval_instance(flow_id);
CREATE INDEX IF NOT EXISTS idx_applicant_id ON approval_instance(applicant_id);
CREATE INDEX IF NOT EXISTS idx_status ON approval_instance(status);
CREATE INDEX IF NOT EXISTS idx_business_key ON approval_instance(business_key);
COMMENT ON TABLE approval_instance IS '流程实例表';

-- 流程步骤表
CREATE TABLE IF NOT EXISTS approval_step (
    id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL,
    node_id BIGINT NOT NULL,
    node_no VARCHAR(50) NOT NULL,
    step_no VARCHAR(50) NOT NULL,
    assignee_id BIGINT NOT NULL,
    assignee_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    action VARCHAR(20),
    opinion TEXT,
    attachments JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    delegated_from BIGINT,
    settings JSONB,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_step_instance_id ON approval_step(instance_id);
CREATE INDEX IF NOT EXISTS idx_node_no ON approval_step(node_no);
CREATE INDEX IF NOT EXISTS idx_assignee_id ON approval_step(assignee_id);
CREATE INDEX IF NOT EXISTS idx_step_status ON approval_step(status);
COMMENT ON TABLE approval_step IS '流程步骤表';

-- 审批意见表
CREATE TABLE IF NOT EXISTS approval_opinion (
    id BIGSERIAL PRIMARY KEY,
    step_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    author_name VARCHAR(100),
    opinion_type VARCHAR(20) DEFAULT 'COMMENT',
    content TEXT NOT NULL,
    attachments JSONB,
    is_private BOOLEAN DEFAULT FALSE,
    reply_to BIGINT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_opinion_step_id ON approval_opinion(step_id);
CREATE INDEX IF NOT EXISTS idx_opinion_author_id ON approval_opinion(author_id);
COMMENT ON TABLE approval_opinion IS '审批意见表';

-- 侧边栏菜单
BEGIN;
DELETE FROM sys_menu WHERE title = '审批流' OR parent_id IN (SELECT id FROM sys_menu WHERE title = '审批流');
INSERT INTO sys_menu (title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ('审批流', 'approval', 0, 50, 'ant-design:file-text-outlined', '/approval', 'Layout', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
WITH inserted AS (SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1)
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) 
SELECT id, '流程管理', 'approval:flow:manage', 1, 1, 'ant-design:setting-outlined', '/approval/flow-manage', '/approval/flow/index', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '发起申请', 'approval:start:list', 1, 2, 'ant-design:plus-circle-outlined', '/approval/start-list', '/approval/start/list', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '我的待办', 'approval:todo', 1, 3, 'ant-design:inbox-outlined', '/approval/todo', '/approval/todo/index', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '我发起的', 'approval:initiated', 1, 4, 'ant-design:send-outlined', '/approval/initiated', '/approval/initiated/index', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '流程设计', 'approval:flow:design', 1, 10, 'ant-design:layout-outlined', '/approval/flow-design/:flowId?', '/approval/flow/design', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '流程详情', 'approval:flow:detail', 1, 11, 'ant-design:eye-outlined', '/approval/flow-detail/:flowId', '/approval/flow/detail', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '发起审批', 'approval:start', 1, 12, 'ant-design:form-outlined', '/approval/start', '/approval/start/index', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '审批处理', 'approval:process', 1, 13, 'ant-design:check-circle-outlined', '/approval/process/:stepId', '/approval/todo/process', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted
UNION ALL SELECT id, '审批详情', 'approval:detail', 1, 14, 'ant-design:file-text-outlined', '/approval/detail/:instanceId', '/approval/initiated/detail', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM inserted;
COMMIT;

-- 检查所有表是否创建成功
SELECT 
    '✅ 表结构验证' AS 检查项,
    COUNT(*) AS 表数量
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'approval_flow',
    'approval_flow_node',
    'approval_flow_line',
    'approval_instance',
    'approval_step',
    'approval_opinion'
);

-- 检查菜单是否创建成功
SELECT 
    '✅ 菜单验证' AS 检查项,
    COUNT(*) AS 菜单数量
FROM sys_menu 
WHERE title = '审批流' OR parent_id IN (SELECT id FROM sys_menu WHERE title = '审批流');

-- 显示所有审批流菜单
SELECT 
    '📋 侧边栏菜单列表' AS 说明;
    
SELECT 
    id AS "ID",
    parent_id AS "父ID",
    title AS "标题",
    name AS "路由名",
    path AS "路径",
    CASE WHEN display = 1 THEN '✅ 显示' ELSE '👻 隐藏' END AS "状态",
    sort AS "排序"
FROM sys_menu 
WHERE title = '审批流' OR parent_id IN (SELECT id FROM sys_menu WHERE title = '审批流')
ORDER BY sort;

SELECT '🎉 审批流插件数据库初始化完成！' AS 提示,
       '请刷新页面查看侧边栏"审批流"菜单' AS 说明;
