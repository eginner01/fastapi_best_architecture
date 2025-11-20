-- 在fba数据库中创建审批流表
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
ALTER DATABASE fba CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fba;

-- 1. 创建流程定义表
CREATE TABLE IF NOT EXISTS tbl_flow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_no VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tbl_flow_node (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    order_num INT NOT NULL,
    node_type ENUM('SINGLE', 'AND', 'OR') DEFAULT 'SINGLE',
    is_first BOOLEAN DEFAULT FALSE,
    is_final BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES tbl_flow(id)
);


CREATE TABLE IF NOT EXISTS tbl_flow_line (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_id INT NOT NULL,
    from_node_id INT NOT NULL,
    to_node_id INT NOT NULL,
    `condition` VARCHAR(255),
    priority INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES tbl_flow(id),
    FOREIGN KEY (from_node_id) REFERENCES tbl_flow_node(id),
    FOREIGN KEY (to_node_id) REFERENCES tbl_flow_node(id)
);

-- 2. 创建流程实例表
CREATE TABLE IF NOT EXISTS tbl_instance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_id INT NOT NULL,
    applicant_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED') DEFAULT 'PENDING',
    current_node_id INT,
    business_key VARCHAR(100),
    form_data JSON,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES tbl_flow(id),
    FOREIGN KEY (current_node_id) REFERENCES tbl_flow_node(id)
);

CREATE TABLE IF NOT EXISTS tbl_step (
    id INT PRIMARY KEY AUTO_INCREMENT,
    instance_id INT NOT NULL,
    node_id INT NOT NULL,
    assignee_id INT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'DELEGATED') DEFAULT 'PENDING',
    opinion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES tbl_instance(id),
    FOREIGN KEY (node_id) REFERENCES tbl_flow_node(id)
);

CREATE TABLE IF NOT EXISTS tbl_opinion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    step_id INT NOT NULL,
    author_id INT NOT NULL,
    content TEXT NOT NULL,
    attachments JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (step_id) REFERENCES tbl_step(id)
);

-- 3. 创建业务关联表
CREATE TABLE IF NOT EXISTS tbl_role_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    department_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_flow_node_flow_id ON tbl_flow_node(flow_id);
CREATE INDEX IF NOT EXISTS idx_flow_node_order ON tbl_flow_node(flow_id, order_num);
CREATE INDEX IF NOT EXISTS idx_flow_line_flow_id ON tbl_flow_line(flow_id);
CREATE INDEX IF NOT EXISTS idx_flow_line_from_node ON tbl_flow_line(from_node_id);
CREATE INDEX IF NOT EXISTS idx_flow_line_to_node ON tbl_flow_line(to_node_id);
CREATE INDEX IF NOT EXISTS idx_instance_flow_id ON tbl_instance(flow_id);
CREATE INDEX IF NOT EXISTS idx_instance_applicant ON tbl_instance(applicant_id);
CREATE INDEX IF NOT EXISTS idx_instance_status ON tbl_instance(status);
CREATE INDEX IF NOT EXISTS idx_instance_current_node ON tbl_instance(current_node_id);
CREATE INDEX IF NOT EXISTS idx_instance_business_key ON tbl_instance(business_key);
CREATE INDEX IF NOT EXISTS idx_step_instance ON tbl_step(instance_id);
CREATE INDEX IF NOT EXISTS idx_step_node ON tbl_step(node_id);
CREATE INDEX IF NOT EXISTS idx_step_assignee ON tbl_step(assignee_id);
CREATE INDEX IF NOT EXISTS idx_step_status ON tbl_step(status);
CREATE INDEX IF NOT EXISTS idx_opinion_step ON tbl_opinion(step_id);
CREATE INDEX IF NOT EXISTS idx_opinion_author ON tbl_opinion(author_id);
CREATE INDEX IF NOT EXISTS idx_role_user_role ON tbl_role_user(role_name);
CREATE INDEX IF NOT EXISTS idx_role_user_user ON tbl_role_user(user_id);
CREATE INDEX IF NOT EXISTS idx_role_user_department ON tbl_role_user(department_id);

-- 5. 添加数据完整性约束
ALTER TABLE tbl_flow_node ADD UNIQUE KEY IF NOT EXISTS uk_flow_node_order (flow_id, order_num);

-- 6. 插入示例数据
INSERT IGNORE INTO tbl_flow (flow_no, name, description, is_active) VALUES
('LEAVE_001', 'Leave Application Process', 'Employee leave application process for annual leave, sick leave, personal leave, etc.', TRUE),
('REIMBURSE_001', 'Expense Reimbursement Process', 'Employee expense reimbursement application and approval process', TRUE),
('PURCHASE_001', 'Purchase Request Process', 'Company procurement request approval process', TRUE);

INSERT IGNORE INTO tbl_flow_node (flow_id, name, role, order_num, node_type, is_first, is_final) VALUES
(1, 'Submit Application', 'employee', 1, 'SINGLE', TRUE, FALSE),
(1, 'Direct Supervisor Approval', 'supervisor', 2, 'SINGLE', FALSE, FALSE),
(1, 'Department Manager Approval', 'department_manager', 3, 'SINGLE', FALSE, FALSE),
(1, 'HR Record', 'hr', 4, 'SINGLE', FALSE, TRUE);

INSERT IGNORE INTO tbl_flow_line (flow_id, from_node_id, to_node_id, condition_expr, priority) VALUES
(1, 1, 2, 'result == "SUBMITTED"', 0),
(1, 2, 3, 'result == "APPROVED"', 0),
(1, 3, 4, 'result == "APPROVED"', 0),
(1, 2, 1, 'result == "REJECTED"', 0),
(1, 3, 1, 'result == "REJECTED"', 0);

INSERT IGNORE INTO tbl_role_user (role_name, user_id, department_id) VALUES
('department_manager', 101, 1),
('department_manager', 102, 2),
('supervisor', 201, 1),
('supervisor', 202, 2),
('hr', 301, NULL),
('hr', 302, NULL);

-- 7. Verify creation results
SELECT 'Table creation completed, tables in current database:' AS 'Execution Result';
SHOW TABLES;

SELECT 'Record counts for each table:' AS 'Data Statistics';
SELECT 'tbl_flow' AS table_name, COUNT(*) AS record_count FROM tbl_flow
UNION ALL
SELECT 'tbl_flow_node', COUNT(*) FROM tbl_flow_node
UNION ALL
SELECT 'tbl_flow_line', COUNT(*) FROM tbl_flow_line
UNION ALL
SELECT 'tbl_role_user', COUNT(*) FROM tbl_role_user;