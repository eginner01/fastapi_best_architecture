-- ============================================
-- 审批流插件数据库初始化脚本 (MySQL)
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
CREATE TABLE IF NOT EXISTS `approval_flow` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `flow_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '流程业务编号',
    `name` VARCHAR(100) NOT NULL COMMENT '流程名称',
    `description` TEXT COMMENT '流程详细描述',
    `icon` VARCHAR(100) COMMENT '流程图标',
    `category` VARCHAR(50) COMMENT '流程分类',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '流程是否激活',
    `version` INT DEFAULT 1 COMMENT '流程版本号',
    `is_published` BOOLEAN DEFAULT FALSE COMMENT '是否已发布',
    `form_schema` JSON COMMENT '表单JSON Schema定义',
    `settings` JSON COMMENT '流程配置',
    `created_by` BIGINT NOT NULL COMMENT '创建者用户ID',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_flow_no` (`flow_no`),
    INDEX `idx_category` (`category`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批流程表';

-- 流程节点表
CREATE TABLE IF NOT EXISTS `approval_flow_node` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `flow_id` BIGINT NOT NULL COMMENT '所属流程ID',
    `node_no` VARCHAR(50) NOT NULL COMMENT '节点编号',
    `name` VARCHAR(100) NOT NULL COMMENT '节点名称',
    `node_type` VARCHAR(20) DEFAULT 'APPROVAL' COMMENT '节点类型',
    `approval_type` VARCHAR(20) DEFAULT 'SINGLE' COMMENT '审批类型',
    `assignee_type` VARCHAR(20) DEFAULT 'ROLE' COMMENT '审批人类型',
    `assignee_value` VARCHAR(500) COMMENT '审批人值',
    `form_permissions` JSON COMMENT '表单权限配置',
    `operation_permissions` JSON COMMENT '操作权限配置',
    `position_x` FLOAT DEFAULT 0 COMMENT '节点X坐标',
    `position_y` FLOAT DEFAULT 0 COMMENT '节点Y坐标',
    `order_num` INT DEFAULT 0 COMMENT '节点顺序号',
    `is_first` BOOLEAN DEFAULT FALSE COMMENT '是否为流程起始节点',
    `is_final` BOOLEAN DEFAULT FALSE COMMENT '是否为流程结束节点',
    `settings` JSON COMMENT '节点配置',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_flow_id` (`flow_id`),
    INDEX `idx_order_num` (`order_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程节点表';

-- 流程线表
CREATE TABLE IF NOT EXISTS `approval_flow_line` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `flow_id` BIGINT NOT NULL COMMENT '所属流程ID',
    `line_no` VARCHAR(50) NOT NULL COMMENT '流程线编号',
    `from_node_id` BIGINT NOT NULL COMMENT '起始节点ID',
    `to_node_id` BIGINT NOT NULL COMMENT '目标节点ID',
    `condition_type` VARCHAR(20) DEFAULT 'NONE' COMMENT '条件类型',
    `condition_expression` VARCHAR(500) COMMENT '条件表达式',
    `priority` INT DEFAULT 0 COMMENT '优先级',
    `label` VARCHAR(100) COMMENT '连线标签',
    `settings` JSON COMMENT '连线配置',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_flow_id` (`flow_id`),
    INDEX `idx_from_node` (`from_node_id`),
    INDEX `idx_priority` (`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程线表';

-- 流程实例表
CREATE TABLE IF NOT EXISTS `approval_instance` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `instance_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '流程实例编号',
    `flow_id` BIGINT NOT NULL COMMENT '关联流程定义ID',
    `flow_version` INT DEFAULT 1 COMMENT '使用的流程版本号',
    `applicant_id` BIGINT NOT NULL COMMENT '申请人用户ID',
    `title` VARCHAR(255) NOT NULL COMMENT '审批实例标题',
    `status` VARCHAR(20) DEFAULT 'PENDING' COMMENT '实例状态',
    `current_node_id` BIGINT COMMENT '当前所处节点ID',
    `business_key` VARCHAR(100) COMMENT '关联业务数据的唯一键',
    `business_type` VARCHAR(50) COMMENT '业务类型',
    `form_data` JSON COMMENT '表单提交数据',
    `started_at` TIMESTAMP NOT NULL COMMENT '流程开始时间',
    `ended_at` TIMESTAMP NULL COMMENT '流程结束时间',
    `duration` INT COMMENT '流程耗时(秒)',
    `urgency` VARCHAR(20) DEFAULT 'NORMAL' COMMENT '紧急程度',
    `tags` JSON COMMENT '标签',
    `attachments` JSON COMMENT '附件信息',
    `settings` JSON COMMENT '实例配置',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_instance_no` (`instance_no`),
    INDEX `idx_flow_id` (`flow_id`),
    INDEX `idx_applicant_id` (`applicant_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_business_key` (`business_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程实例表';

-- 流程步骤表
CREATE TABLE IF NOT EXISTS `approval_step` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `instance_id` BIGINT NOT NULL COMMENT '所属流程实例ID',
    `node_id` BIGINT NOT NULL COMMENT '关联流程节点ID',
    `node_no` VARCHAR(50) NOT NULL COMMENT '节点编号',
    `step_no` VARCHAR(50) NOT NULL COMMENT '步骤编号',
    `assignee_id` BIGINT NOT NULL COMMENT '指定审批人用户ID',
    `assignee_name` VARCHAR(100) COMMENT '审批人姓名',
    `status` VARCHAR(20) DEFAULT 'PENDING' COMMENT '步骤状态',
    `action` VARCHAR(20) COMMENT '执行操作',
    `opinion` TEXT COMMENT '审批意见',
    `attachments` JSON COMMENT '附件信息',
    `started_at` TIMESTAMP NOT NULL COMMENT '步骤开始时间',
    `completed_at` TIMESTAMP NULL COMMENT '步骤完成时间',
    `duration` INT COMMENT '处理耗时(秒)',
    `is_read` BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    `delegated_from` BIGINT COMMENT '转交来源用户ID',
    `settings` JSON COMMENT '步骤配置',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_instance_id` (`instance_id`),
    INDEX `idx_node_no` (`node_no`),
    INDEX `idx_assignee_id` (`assignee_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程步骤表';

-- 审批意见表
CREATE TABLE IF NOT EXISTS `approval_opinion` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `step_id` BIGINT NOT NULL COMMENT '关联流程步骤ID',
    `author_id` BIGINT NOT NULL COMMENT '意见作者用户ID',
    `author_name` VARCHAR(100) COMMENT '作者姓名',
    `opinion_type` VARCHAR(20) DEFAULT 'COMMENT' COMMENT '意见类型',
    `content` TEXT NOT NULL COMMENT '意见内容',
    `attachments` JSON COMMENT '附件信息',
    `is_private` BOOLEAN DEFAULT FALSE COMMENT '是否为私密意见',
    `reply_to` BIGINT COMMENT '回复的意见ID',
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_step_id` (`step_id`),
    INDEX `idx_author_id` (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批意见表';

-- 侧边栏
START TRANSACTION;
DELETE FROM sys_menu WHERE title = '审批流' OR parent_id IN (SELECT id FROM (SELECT id FROM sys_menu WHERE title = '审批流') AS temp);
INSERT INTO sys_menu (title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES ('审批流', 'approval', 0, 50, 'ant-design:file-text-outlined', '/approval', 'Layout', 1, 1, 1, NOW(), NOW());
SET @pid = LAST_INSERT_ID();
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '流程管理', 'approval:flow:manage', 1, 1, 'ant-design:setting-outlined', '/approval/flow-manage', '/approval/flow/index', 1, 1, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '发起申请', 'approval:start:list', 1, 2, 'ant-design:plus-circle-outlined', '/approval/start-list', '/approval/start/list', 1, 1, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '我的待办', 'approval:todo', 1, 3, 'ant-design:inbox-outlined', '/approval/todo', '/approval/todo/index', 1, 1, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '我发起的', 'approval:initiated', 1, 4, 'ant-design:send-outlined', '/approval/initiated', '/approval/initiated/index', 1, 1, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '流程设计', 'approval:flow:design', 1, 10, 'ant-design:layout-outlined', '/approval/flow-design/:flowId?', '/approval/flow/design', 0, 0, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '流程详情', 'approval:flow:detail', 1, 11, 'ant-design:eye-outlined', '/approval/flow-detail/:flowId', '/approval/flow/detail', 0, 0, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '发起审批', 'approval:start', 1, 12, 'ant-design:form-outlined', '/approval/start', '/approval/start/index', 0, 0, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '审批处理', 'approval:process', 1, 13, 'ant-design:check-circle-outlined', '/approval/process/:stepId', '/approval/todo/process', 0, 0, 1, NOW(), NOW());
INSERT INTO sys_menu (parent_id, title, name, type, sort, icon, path, component, display, cache, status, created_time, updated_time) VALUES (@pid, '审批详情', 'approval:detail', 1, 14, 'ant-design:file-text-outlined', '/approval/detail/:instanceId', '/approval/initiated/detail', 0, 0, 1, NOW(), NOW());
SELECT id, parent_id, title, name, path, component, display FROM sys_menu WHERE title = '审批流' OR parent_id = @pid ORDER BY sort;
COMMIT;

-- 检查所有表是否创建成功
SELECT 
    '✅ 表结构验证' AS 检查项,
    COUNT(*) AS 表数量
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME IN (
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
