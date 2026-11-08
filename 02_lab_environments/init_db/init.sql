-- ==============================================================================
-- AI Native Business Workflow - ITSM 및 엔터프라이즈 운영 실습용 초기화 SQL
-- 
-- 주요 테이블:
--   1. customers         : 고객사별 계약 등급(VIP/Enterprise/Standard) 및 SLA 정책
--   2. incident_tickets  : 장애 티켓 정보 (심각도, 카테고리, 상태)
--   3. audit_logs        : AI 에이전트 및 관리자 조치 감사 추적 로그
--   4. knowledge_vectors : Week 2 pgvector 실습용 샘플 벡터 저장소 (1024차원 bge-m3 호환)
-- ==============================================================================

-- 1. pgvector 및 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 2. customers 테이블 정의 및 인덱스 생성
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contract_tier VARCHAR(20) NOT NULL CHECK (contract_tier IN ('VIP', 'Enterprise', 'Standard')),
    sla_response_minutes INT NOT NULL,
    account_manager_email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_tier ON customers(contract_tier);

-- ------------------------------------------------------------------------------
-- 3. incident_tickets 테이블 정의 및 인덱스 생성
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS incident_tickets CASCADE;
CREATE TABLE incident_tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    category VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Open', 'In_Progress', 'Resolved', 'Closed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tickets_customer_id ON incident_tickets(customer_id);
CREATE INDEX idx_tickets_severity ON incident_tickets(severity);
CREATE INDEX idx_tickets_status ON incident_tickets(status);

-- ------------------------------------------------------------------------------
-- 4. audit_logs 테이블 정의 및 인덱스 생성
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS audit_logs CASCADE;
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    payload_json JSONB NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_workflow ON audit_logs(workflow_name);
CREATE INDEX idx_audit_logs_action ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_executed_at ON audit_logs(executed_at DESC);

-- ------------------------------------------------------------------------------
-- 5. knowledge_vectors (Week 2 pgvector 선택 실습용 1024차원 임베딩 테이블)
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS knowledge_vectors CASCADE;
CREATE TABLE knowledge_vectors (
    id BIGSERIAL PRIMARY KEY,
    doc_id VARCHAR(100) NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1024) -- BAAI/bge-m3 모델 기준 1024차원
);

CREATE INDEX idx_knowledge_vectors_doc ON knowledge_vectors(doc_id);

-- ==============================================================================
-- 시드 데이터 주입 (현실적인 한국어 엔터프라이즈 운영 시나리오)
-- ==============================================================================

-- 1. customers 시드 데이터 (10개 고객사)
INSERT INTO customers (customer_id, company_name, contract_tier, sla_response_minutes, account_manager_email, created_at)
VALUES
('CUST-1001', '(주)대한전자', 'VIP', 15, 'am_daehan@enterprise.internal', NOW() - INTERVAL '180 DAY'),
('CUST-1002', '(주)미래파이낸셜', 'VIP', 15, 'am_mirae@enterprise.internal', NOW() - INTERVAL '150 DAY'),
('CUST-1003', '넥서스로지스틱스(주)', 'Enterprise', 60, 'am_nexus@enterprise.internal', NOW() - INTERVAL '120 DAY'),
('CUST-1004', '한빛바이오랩', 'Enterprise', 60, 'am_hanbit@enterprise.internal', NOW() - INTERVAL '90 DAY'),
('CUST-1005', '알파소프트웨어솔루션', 'Enterprise', 60, 'am_alpha@enterprise.internal', NOW() - INTERVAL '80 DAY'),
('CUST-1006', '글로벌커머스네트워크', 'VIP', 15, 'am_global@enterprise.internal', NOW() - INTERVAL '70 DAY'),
('CUST-1007', '성우모빌리티시스템', 'Standard', 240, 'am_sungwoo@enterprise.internal', NOW() - INTERVAL '60 DAY'),
('CUST-1008', '에듀포커스인터내셔널', 'Standard', 240, 'am_edufocus@enterprise.internal', NOW() - INTERVAL '40 DAY'),
('CUST-1009', '핀테크허브글로벌', 'VIP', 15, 'am_fintech@enterprise.internal', NOW() - INTERVAL '30 DAY'),
('CUST-1010', '메디컬인포케어', 'Standard', 240, 'am_medicare@enterprise.internal', NOW() - INTERVAL '15 DAY');

-- 2. incident_tickets 시드 데이터 (10개 장애 및 인시던트 티켓)
INSERT INTO incident_tickets (ticket_id, customer_id, severity, category, summary, status, created_at)
VALUES
('TKT-2026-001', 'CUST-1001', 'Critical', 'DATABASE', '대규모 결제 이벤트 중 주문 RDBMS 커넥션 풀 점유율 96% 급증으로 인한 서비스 지연 및 500 에러 발생', 'Open', NOW() - INTERVAL '12 MINUTE'),
('TKT-2026-002', 'CUST-1002', 'Critical', 'AUTHENTICATION', '통합 사내 SSO 및 OAuth2 인증 게이트웨이 응답 지연(504 Gateway Timeout)으로 모바일 뱅킹 로그인 차단', 'In_Progress', NOW() - INTERVAL '25 MINUTE'),
('TKT-2026-003', 'CUST-1003', 'High', 'MEMORY_LEAK', '배송 상태 추적 API 컨테이너 힙 메모리 점유율 91% 도달 및 Full GC 주기 4초 단축 현상 관측', 'Open', NOW() - INTERVAL '48 MINUTE'),
('TKT-2026-004', 'CUST-1006', 'Critical', 'DATABASE', '블랙프라이데이 프로모션 중 메인 결제 DB 커넥션 풀 고갈(95%) 및 트랜잭션 타임아웃 발생', 'Open', NOW() - INTERVAL '8 MINUTE'),
('TKT-2026-005', 'CUST-1004', 'Medium', 'NETWORK_LATENCY', '유전체 시퀀싱 데이터 전송 배치 작업 중 간헐적 패킷 드롭 및 전송 속도 60% 급감', 'In_Progress', NOW() - INTERVAL '2 HOUR'),
('TKT-2026-006', 'CUST-1005', 'Low', 'CONFIGURATION', '개발 스테이징 환경 신규 마이크로서비스 CORS 화이트리스트 미등록으로 인한 테스트 호출 실패', 'Resolved', NOW() - INTERVAL '6 HOUR'),
('TKT-2026-007', 'CUST-1009', 'High', 'SECURITY_ALERT', '이상 해외 IP 대역에서 계좌 실명인증 엔드포인트 대상 초당 1,200회 무차별 대입(Brute-force) 의심 호출 감지', 'Open', NOW() - INTERVAL '18 MINUTE'),
('TKT-2026-008', 'CUST-1007', 'Medium', 'BATCH_JOB', '월 마감 차량 관제 정산 배치 프로세스 중 일시적 외래키 정합성 불일치로 작업 실패', 'Resolved', NOW() - INTERVAL '14 HOUR'),
('TKT-2026-009', 'CUST-1008', 'Low', 'UI_BUG', '수강생 성적 리포트 PDF 출력 모듈에서 한글 글꼴 렌더링 깨짐 및 페이지 넘김 오류', 'Closed', NOW() - INTERVAL '1 DAY'),
('TKT-2026-010', 'CUST-1001', 'High', 'STORAGE_CAPACITY', '트랜잭션 감사 아카이브 저장소 볼륨 디스크 사용률 88% 돌파 (경고 임계치 85% 초과)', 'Resolved', NOW() - INTERVAL '2 DAY');

-- 3. audit_logs 시드 데이터 (7개 감사 로그 기록)
INSERT INTO audit_logs (workflow_name, action_type, actor, payload_json, executed_at)
VALUES
('System_Bootstrap', 'PROVISION_INFRA', 'admin_sys', '{"status": "completed", "cluster": "k8s-prod-seoul", "nodes": 12}'::jsonb, NOW() - INTERVAL '3 DAY'),
('Health_Monitor_Daemon', 'METRIC_THRESHOLD_ALERT', 'system_daemon', '{"server_id": "db-primary-01", "metric": "db_connection_pool_usage", "value": 94.2, "status": "critical"}'::jsonb, NOW() - INTERVAL '12 MINUTE'),
('ITSM_Auto_Triage_Workflow', 'PARSE_AND_CLASSIFY', 'n8n_ai_agent_w1', '{"ticket_id": "TKT-2026-001", "classified_severity": "Critical", "assigned_team": "Database_SRE"}'::jsonb, NOW() - INTERVAL '10 MINUTE'),
('Security_Guardrail_Agent', 'IP_BLOCK_RECOMMENDATION', 'n8n_guardrail_w4', '{"target_ip_range": "198.51.100.0/24", "threat_level": "High", "rule_id": "SEC-R-992"}'::jsonb, NOW() - INTERVAL '15 MINUTE'),
('Emergency_Remediation_Workflow', 'REQUEST_HITL_APPROVAL', 'n8n_agent_w4', '{"action": "reset-db-pool", "server_id": "db-primary-01", "approver_role": "Lead_SRE", "ticket_id": "TKT-2026-001"}'::jsonb, NOW() - INTERVAL '9 MINUTE'),
('Manual_Operations_Log', 'RESOLVE_TICKET', 'engineer_kim@enterprise.internal', '{"ticket_id": "TKT-2026-008", "resolution": "Re-executed batch job with updated foreign key constraints"}'::jsonb, NOW() - INTERVAL '13 HOUR'),
('Storage_Capacity_Manager', 'AUTO_CLEANUP_TEMP_FILES', 'cron_automation', '{"volume": "/mnt/audit_data", "freed_gb": 42.5, "post_usage_pct": 74.1}'::jsonb, NOW() - INTERVAL '1 DAY');
