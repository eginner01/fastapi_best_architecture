-- ============================================
-- 审批流插件数据库初始化脚本 (SQLite)
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

PRAGMA foreign_keys = ON;

-- 流程表
CREATE TABLE IF NOT EXISTS approval_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_no TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    category TEXT,
    is_active INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1,
    is_published INTEGER DEFAULT 0,
    form_schema TEXT,
    settings TEXT,
    created_by INTEGER NOT NULL,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_flow_no ON approval_flow(flow_no);
CREATE INDEX IF NOT EXISTS idx_category ON approval_flow(category);
CREATE INDEX IF NOT EXISTS idx_is_active ON approval_flow(is_active);

-- 流程节点表
CREATE TABLE IF NOT EXISTS approval_flow_node (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id INTEGER NOT NULL,
    node_no TEXT NOT NULL,
    name TEXT NOT NULL,
    node_type TEXT DEFAULT 'APPROVAL',
    approval_type TEXT DEFAULT 'SINGLE',
    assignee_type TEXT DEFAULT 'ROLE',
    assignee_value TEXT,
    form_permissions TEXT,
    operation_permissions TEXT,
    position_x REAL DEFAULT 0,
    position_y REAL DEFAULT 0,
    order_num INTEGER DEFAULT 0,
    is_first INTEGER DEFAULT 0,
    is_final INTEGER DEFAULT 0,
    settings TEXT,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_flow_id ON approval_flow_node(flow_id);
CREATE INDEX IF NOT EXISTS idx_order_num ON approval_flow_node(order_num);

-- 流程线表
CREATE TABLE IF NOT EXISTS approval_flow_line (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id INTEGER NOT NULL,
    line_no TEXT NOT NULL,
    from_node_id INTEGER NOT NULL,
    to_node_id INTEGER NOT NULL,
    condition_type TEXT DEFAULT 'NONE',
    condition_expression TEXT,
    priority INTEGER DEFAULT 0,
    label TEXT,
    settings TEXT,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_flow_line_flow_id ON approval_flow_line(flow_id);
CREATE INDEX IF NOT EXISTS idx_from_node ON approval_flow_line(from_node_id);
CREATE INDEX IF NOT EXISTS idx_priority ON approval_flow_line(priority);

-- 流程实例表
CREATE TABLE IF NOT EXISTS approval_instance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_no TEXT NOT NULL UNIQUE,
    flow_id INTEGER NOT NULL,
    flow_version INTEGER DEFAULT 1,
    applicant_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    current_node_id INTEGER,
    business_key TEXT,
    business_type TEXT,
    form_data TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration INTEGER,
    urgency TEXT DEFAULT 'NORMAL',
    tags TEXT,
    attachments TEXT,
    settings TEXT,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_instance_no ON approval_instance(instance_no);
CREATE INDEX IF NOT EXISTS idx_instance_flow_id ON approval_instance(flow_id);
CREATE INDEX IF NOT EXISTS idx_applicant_id ON approval_instance(applicant_id);
CREATE INDEX IF NOT EXISTS idx_status ON approval_instance(status);
CREATE INDEX IF NOT EXISTS idx_business_key ON approval_instance(business_key);

-- 流程步骤表
CREATE TABLE IF NOT EXISTS approval_step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    node_no TEXT NOT NULL,
    step_no TEXT NOT NULL,
    assignee_id INTEGER NOT NULL,
    assignee_name TEXT,
    status TEXT DEFAULT 'PENDING',
    action TEXT,
    opinion TEXT,
    attachments TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    duration INTEGER,
    is_read INTEGER DEFAULT 0,
    delegated_from INTEGER,
    settings TEXT,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_step_instance_id ON approval_step(instance_id);
CREATE INDEX IF NOT EXISTS idx_node_no ON approval_step(node_no);
CREATE INDEX IF NOT EXISTS idx_assignee_id ON approval_step(assignee_id);
CREATE INDEX IF NOT EXISTS idx_step_status ON approval_step(status);

-- 审批意见表
CREATE TABLE IF NOT EXISTS approval_opinion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    author_name TEXT,
    opinion_type TEXT DEFAULT 'COMMENT',
    content TEXT NOT NULL,
    attachments TEXT,
    is_private INTEGER DEFAULT 0,
    reply_to INTEGER,
    created_time TEXT DEFAULT (datetime('now')),
    updated_time TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_opinion_step_id ON approval_opinion(step_id);
CREATE INDEX IF NOT EXISTS idx_opinion_author_id ON approval_opinion(author_id);

-- 侧边栏菜单
BEGIN TRANSACTION;
DELETE FROM sys_menu WHERE title = '审批流' OR parent_id IN (SELECT id FROM sys_menu WHERE title = '审批流');
INSERT INTO sys_menu (title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ('审批流', 'approval', 0, 50, 'ant-design:file-text-outlined', '/approval', 'Layout', 1, 1, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '流程管理', 'approval:flow:manage', 1, 1, 'ant-design:setting-outlined', '/approval/flow-manage', '/approval/flow/index', 1, 1, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '发起申请', 'approval:start:list', 1, 2, 'ant-design:plus-circle-outlined', '/approval/start-list', '/approval/start/list', 1, 1, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '我的待办', 'approval:todo', 1, 3, 'ant-design:inbox-outlined', '/approval/todo', '/approval/todo/index', 1, 1, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '我发起的', 'approval:initiated', 1, 4, 'ant-design:send-outlined', '/approval/initiated', '/approval/initiated/index', 1, 1, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '流程设计', 'approval:flow:design', 1, 10, 'ant-design:layout-outlined', '/approval/flow-design/:flowId?', '/approval/flow/design', 0, 0, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '流程详情', 'approval:flow:detail', 1, 11, 'ant-design:eye-outlined', '/approval/flow-detail/:flowId', '/approval/flow/detail', 0, 0, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '发起审批', 'approval:start', 1, 12, 'ant-design:form-outlined', '/approval/start', '/approval/start/index', 0, 0, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '审批处理', 'approval:process', 1, 13, 'ant-design:check-circle-outlined', '/approval/process/:stepId', '/approval/todo/process', 0, 0, 1, datetime('now'), datetime('now'));
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ((SELECT id FROM sys_menu WHERE title = '审批流' ORDER BY id DESC LIMIT 1), '审批详情', 'approval:detail', 1, 14, 'ant-design:file-text-outlined', '/approval/detail/:instanceId', '/approval/initiated/detail', 0, 0, 1, datetime('now'), datetime('now'));
COMMIT;

-- 检查所有表是否创建成功
SELECT 
    '✅ 表结构验证' AS 检查项,
    COUNT(*) AS 表数量
FROM sqlite_master 
WHERE type = 'table' 
  AND name IN (
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
    id AS ID,
    parent_id AS 父ID,
    title AS 标题,
    name AS 路由名,
    path AS 路径,
    CASE WHEN display = 1 THEN '✅ 显示' ELSE '👻 隐藏' END AS 状态,
    sort AS 排序
FROM sys_menu 
WHERE title = '审批流' OR parent_id IN (SELECT id FROM sys_menu WHERE title = '审批流')
ORDER BY sort;

SELECT '🎉 审批流插件数据库初始化完成！' AS 提示,
       '请刷新页面查看侧边栏"审批流"菜单' AS 说明;
