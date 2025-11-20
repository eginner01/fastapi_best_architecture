-- ============================================
-- Complete Approval Workflow Menu Configuration SQL
-- ============================================

-- 1. Delete old approval workflow menus (if exists)
DELETE FROM sys_menu WHERE title = 'Approval Workflow' OR parent_id IN (SELECT id FROM sys_menu WHERE title = 'Approval Workflow');

-- 2. Insert main approval workflow menu
INSERT INTO sys_menu (title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES ('Approval Workflow', 'Approval', 1, 50, 'file-text', '/approval', 'Layout', 0, 1, 1, 'Approval Workflow Management System', NOW(), NOW());

-- Get approval workflow main menu ID
SET @approval_parent_id = LAST_INSERT_ID();

-- 3. Insert submenu - Flow Management
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Flow Management', 'FlowManagement', 2, 1, 'settings', '/approval/flow-manage', '/approval/flow/index', 0, 1, 1, 'Manage approval flow templates', NOW(), NOW());

-- 4. Insert submenu - Flow Design (hidden, accessed via Flow Management)
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Flow Design', 'FlowDesign', 2, 2, 'layout', '/approval/flow-design', '/approval/flow/design', 1, 0, 1, 'Flow designer (hidden)', NOW(), NOW());

-- 5. Insert submenu - Flow Detail (hidden, accessed via Flow Management)
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Flow Detail', 'FlowDetail', 2, 3, 'file', '/approval/flow-detail/:flowId', '/approval/flow/detail', 1, 0, 1, 'Flow detail page (hidden)', NOW(), NOW());

-- 6. Insert submenu - Start Approval (hidden, accessed via Flow Management)
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Start Approval', 'StartApproval', 2, 4, 'plus-circle', '/approval/start', '/approval/start/index', 1, 0, 1, 'Start approval request (hidden)', NOW(), NOW());

-- 7. Insert submenu - My Todo
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'My Todo', 'TodoList', 2, 5, 'inbox', '/approval/todo', '/approval/todo/index', 0, 1, 1, 'Pending approval tasks', NOW(), NOW());

-- 8. Insert submenu - My Initiated
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'My Initiated', 'InitiatedList', 2, 6, 'send', '/approval/initiated', '/approval/initiated/index', 0, 1, 1, 'My initiated approval requests', NOW(), NOW());

-- 9. Insert submenu - Process Approval (hidden, accessed via Todo list)
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Process Approval', 'ProcessApproval', 2, 7, 'check-circle', '/approval/process/:stepId', '/approval/todo/process', 1, 0, 1, 'Approval processing page (hidden)', NOW(), NOW());

-- 10. Insert submenu - Instance Detail (hidden, accessed via My Initiated)
INSERT INTO sys_menu (parent_id, title, name, level, sort, icon, path, component, is_hidden, cache, status, remark, created_time, updated_time)
VALUES (@approval_parent_id, 'Approval Detail', 'InstanceDetail', 2, 8, 'eye', '/approval/detail/:instanceId', '/approval/initiated/detail', 1, 0, 1, 'Approval instance detail (hidden)', NOW(), NOW());

-- 11. Query results for verification
SELECT 
    m.id,
    m.parent_id,
    m.title,
    m.name,
    m.level,
    m.sort,
    m.icon,
    m.path,
    m.component,
    m.is_hidden,
    m.cache,
    m.status,
    CASE 
        WHEN m.parent_id IS NULL THEN 'Main Menu'
        WHEN m.is_hidden = 1 THEN 'Hidden Menu'
        ELSE 'Visible Menu'
    END AS menu_type
FROM sys_menu m
WHERE m.title = 'Approval Workflow' 
   OR m.parent_id IN (SELECT id FROM sys_menu WHERE title = 'Approval Workflow')
ORDER BY m.level, m.sort;

-- ============================================
-- Menu Description
-- ============================================
-- Main Menu (Visible):
--   Approval Workflow (/approval)
--
-- Submenus (Visible):
--   1. Flow Management (/approval/flow-manage) - Manage approval flow templates
--   2. My Todo (/approval/todo) - View pending approval tasks
--   3. My Initiated (/approval/initiated) - View my initiated approval requests
--
-- Submenus (Hidden, for page navigation):
--   1. Flow Design (/approval/flow-design) - Create/edit flows
--   2. Flow Detail (/approval/flow-detail/:flowId) - View flow configuration
--   3. Start Approval (/approval/start) - Start approval request
--   4. Process Approval (/approval/process/:stepId) - Process approval task
--   5. Approval Detail (/approval/detail/:instanceId) - View approval detail
-- ============================================

COMMIT;
