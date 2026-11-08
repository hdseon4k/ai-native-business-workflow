"""
AI Native Business Workflow - Mock Enterprise API Server
사내 인프라 모니터링, 고위험 조치 실행(Runbook), 및 LangGraph 심층 추론 모사 서버
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Mock Enterprise ITSM & Infrastructure API",
    version="1.0.0",
    description="n8n AI Agent 및 Week 1~5 실습 연동용 가상 사내 모니터링/조치/심층추론 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 인메모리 서버 상태 저장소 (실습 중 리셋 조치 실행 시 상태 변화 반영)
# ------------------------------------------------------------------------------
DEFAULT_SERVER_METRICS: Dict[str, Dict[str, Any]] = {
    "db-primary-01": {
        "server_id": "db-primary-01",
        "hostname": "db-cluster-master.internal",
        "role": "PostgreSQL Primary Cluster",
        "cpu_usage_pct": 78.4,
        "memory_usage_pct": 82.5,
        "db_connection_pool_usage": {
            "active_connections": 95,
            "max_connections": 100,
            "idle_connections": 5,
            "waiting_clients": 42,
            "pool_usage_pct": 95.0,
        },
        "status": "critical",
        "description": "메인 RDBMS 커넥션 풀 고갈 직전 (임계치 90% 초과)",
    },
    "app-was-01": {
        "server_id": "app-was-01",
        "hostname": "order-api-prod-01.internal",
        "role": "Order Processing WAS Node 1",
        "cpu_usage_pct": 65.2,
        "memory_usage_pct": 91.8,
        "db_connection_pool_usage": {
            "active_connections": 45,
            "max_connections": 100,
            "idle_connections": 55,
            "waiting_clients": 0,
            "pool_usage_pct": 45.0,
        },
        "status": "degraded",
        "description": "JVM 힙 메모리 점유율 임계치 초과 및 Full GC 지연",
    },
    "auth-api-01": {
        "server_id": "auth-api-01",
        "hostname": "sso-auth-gateway.internal",
        "role": "Enterprise SSO & OAuth2 Gateway",
        "cpu_usage_pct": 34.0,
        "memory_usage_pct": 42.1,
        "db_connection_pool_usage": {
            "active_connections": 22,
            "max_connections": 100,
            "idle_connections": 78,
            "waiting_clients": 0,
            "pool_usage_pct": 22.0,
        },
        "status": "healthy",
        "description": "정상 가동 중",
    },
}

current_server_states: Dict[str, Dict[str, Any]] = {
    k: dict(v) for k, v in DEFAULT_SERVER_METRICS.items()
}


# ------------------------------------------------------------------------------
# Pydantic 모델 정의
# ------------------------------------------------------------------------------
class ResetDbPoolRequest(BaseModel):
    server_id: str = Field(default="db-primary-01", description="대상 데이터베이스 서버 ID")
    reason: str = Field(..., description="조치 실행 사유 및 관련 인시던트 티켓 정보")
    authorized_by: str = Field(..., description="승인자 식별자 (엔지니어 이메일 또는 사번)")
    ticket_id: Optional[str] = Field(None, description="관련 ITSM 티켓 ID (예: TKT-2026-001)")


class ResetDbPoolResponse(BaseModel):
    status: str
    transaction_id: str
    server_id: str
    reclaimed_connections: int
    current_pool_usage_pct: float
    message: str
    executed_at: str


class DeepAgentAnalyzeRequest(BaseModel):
    incident_summary: str = Field(..., description="장애 증상 요약문 또는 고객 문의 내용")
    server_id: Optional[str] = Field("db-primary-01", description="장애 대상 서버 식별자")
    customer_tier: Optional[str] = Field("Standard", description="고객 계약 등급 (VIP, Enterprise, Standard)")
    metrics: Optional[Dict[str, Any]] = Field(None, description="사전 수집된 실시간 메트릭")
    knowledge_context: Optional[str] = Field(None, description="사내 RAG에서 검색된 매뉴얼/SLA 텍스트")


class DeepAgentAnalyzeResponse(BaseModel):
    analysis_id: str
    root_cause_hypothesis: str
    confidence_score: float
    risk_level: str
    requires_human_approval: bool
    sla_response_limit_minutes: int
    recommended_actions: List[Dict[str, Any]]
    execution_plan: Dict[str, Any]
    analyzed_at: str


# ------------------------------------------------------------------------------
# 1. 헬스체크 및 상태 복구 엔드포인트
# ------------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "service": "Mock Enterprise API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/simulation/reset", tags=["Simulation"])
def reset_simulation_state():
    """모의 실습 상태를 초기 장애 발생 상태로 되돌립니다."""
    global current_server_states
    current_server_states = {k: dict(v) for k, v in DEFAULT_SERVER_METRICS.items()}
    return {"status": "success", "message": "모든 가상 서버 메트릭이 초기 장애 상태로 복원되었습니다."}


# ------------------------------------------------------------------------------
# 2. [엔드포인트 1] 서버 실시간 메트릭 조회 (GET)
# ------------------------------------------------------------------------------
@app.get("/api/v1/metrics/{server_id}", tags=["Monitoring"])
def get_server_metrics(
    server_id: str = Path(..., description="조회할 서버 ID (예: db-primary-01, app-was-01, auth-api-01)"),
    force_status: Optional[str] = Query(None, description="테스트용 강제 상태 지정 (healthy, degraded, critical)"),
):
    """
    지정된 사내 서버의 CPU, 메모리, DB 커넥션 풀 가용률 및 종합 상태를 반환합니다.
    """
    if server_id in current_server_states:
        metric = dict(current_server_states[server_id])
    else:
        # 등록되지 않은 임의의 서버 요청 시 기본 healthy 상태로 동적 생성
        metric = {
            "server_id": server_id,
            "hostname": f"{server_id}.internal",
            "role": "General Purpose Instance",
            "cpu_usage_pct": 25.0,
            "memory_usage_pct": 38.0,
            "db_connection_pool_usage": {
                "active_connections": 15,
                "max_connections": 100,
                "idle_connections": 85,
                "waiting_clients": 0,
                "pool_usage_pct": 15.0,
            },
            "status": "healthy",
            "description": "일반 인스턴스 정상 가동 중",
        }

    # 테스트 편의용 파라미터 오버라이드
    if force_status in ["healthy", "degraded", "critical"]:
        metric["status"] = force_status
        if force_status == "critical":
            metric["db_connection_pool_usage"]["pool_usage_pct"] = 96.0
            metric["db_connection_pool_usage"]["active_connections"] = 96
        elif force_status == "healthy":
            metric["db_connection_pool_usage"]["pool_usage_pct"] = 14.0
            metric["db_connection_pool_usage"]["active_connections"] = 14

    metric["timestamp"] = datetime.now(timezone.utc).isoformat()
    return metric


# ------------------------------------------------------------------------------
# 3. [엔드포인트 2] 고위험 조치 실행: DB 커넥션 풀 리셋 (POST)
# ------------------------------------------------------------------------------
@app.post("/api/v1/actions/reset-db-pool", response_model=ResetDbPoolResponse, tags=["Remediation"])
def reset_db_connection_pool(request: ResetDbPoolRequest):
    """
    고위험 자동화 조치: DB 유휴/좀비 커넥션을 일괄 회수하고 커넥션 풀을 초기화합니다.
    HITL(인간 승인)을 거친 후 n8n 또는 운영자에 의해 호출됩니다.
    """
    server_id = request.server_id

    # 서버 상태가 존재하는 경우 healthy로 즉시 전이
    if server_id in current_server_states:
        current_server_states[server_id]["db_connection_pool_usage"]["active_connections"] = 12
        current_server_states[server_id]["db_connection_pool_usage"]["idle_connections"] = 88
        current_server_states[server_id]["db_connection_pool_usage"]["waiting_clients"] = 0
        current_server_states[server_id]["db_connection_pool_usage"]["pool_usage_pct"] = 12.0
        current_server_states[server_id]["status"] = "healthy"
        current_server_states[server_id]["description"] = "DB 커넥션 풀 초기화 완료 및 정상화됨"

    tx_id = f"TX-RST-{uuid.uuid4().hex[:8].upper()}"
    executed_at = datetime.now(timezone.utc).isoformat()

    return ResetDbPoolResponse(
        status="success",
        transaction_id=tx_id,
        server_id=server_id,
        reclaimed_connections=83,
        current_pool_usage_pct=12.0,
        message=(
            f"서버 [{server_id}]의 DB 커넥션 풀 강제 회수 작업이 성공적으로 수행되었습니다. "
            f"(승인자: {request.authorized_by}, 사유: {request.reason})"
        ),
        executed_at=executed_at,
    )


# ------------------------------------------------------------------------------
# 4. [엔드포인트 3] Week 5 하이브리드 연동용 심층 루프 추론 (POST)
# ------------------------------------------------------------------------------
@app.post("/api/v1/deep-agent/analyze", response_model=DeepAgentAnalyzeResponse, tags=["DeepReasoning"])
def deep_agent_analyze(request: DeepAgentAnalyzeRequest):
    """
    Week 5 전용: 복합 장애 상황에서 LangGraph의 순환 상태 머신 추론을 모사하여,
    근본 원인 가설, 위험도 평가, 인간 승인 필요 여부, 단계별 복구 계획을 도출합니다.
    """
    analysis_id = f"ANL-{uuid.uuid4().hex[:8].upper()}"
    summary_lower = request.incident_summary.lower()
    customer_tier = request.customer_tier or "Standard"

    # SLA 기준시간 산출
    sla_map = {"VIP": 15, "Enterprise": 60, "Standard": 240}
    sla_limit = sla_map.get(customer_tier, 240)

    # 장애 유형 및 원인 추론
    if any(k in summary_lower for k in ["커넥션", "db", "database", "connection", "500"]):
        root_cause = "트랜잭션 급증 및 장기 실행 쿼리로 인한 DB 커넥션 풀(Connection Pool) 고갈"
        risk_level = "High" if customer_tier in ["VIP", "Enterprise"] else "Medium"
        requires_approval = True  # 고위험 액션 수반
        actions = [
            {
                "step": 1,
                "action": "check_metrics",
                "endpoint": f"/api/v1/metrics/{request.server_id}",
                "description": "실시간 커넥션 풀 점유율 확인",
            },
            {
                "step": 2,
                "action": "request_hitl_approval",
                "target": "SRE_Lead",
                "description": f"{customer_tier} 고객사 영향도에 따른 DB 커넥션 풀 리셋 승인 요청",
            },
            {
                "step": 3,
                "action": "execute_pool_reset",
                "endpoint": "/api/v1/actions/reset-db-pool",
                "description": "승인 완료 시 커넥션 풀 즉시 초기화 실행",
            },
            {
                "step": 4,
                "action": "notify_account_manager",
                "description": "조치 완료 결과 및 재발 방지 모니터링 로그 발송",
            },
        ]
    elif any(k in summary_lower for k in ["메모리", "leak", "oom", "힙", "heap"]):
        root_cause = "애플리케이션 WAS 컨테이너의 지속적인 힙 메모리 누수 및 Full GC 지연"
        risk_level = "Medium"
        requires_approval = False
        actions = [
            {
                "step": 1,
                "action": "capture_heap_dump",
                "description": "진단용 힙 덤프 수집",
            },
            {
                "step": 2,
                "action": "rolling_restart",
                "description": "WAS 파드 무중단 롤링 재기동",
            },
        ]
    else:
        root_cause = "일반 서비스 지연 및 일시적 네트워크 병목 현상"
        risk_level = "Low"
        requires_approval = False
        actions = [
            {
                "step": 1,
                "action": "monitor_traffic",
                "description": "트래픽 추이 15분간 모니터링",
            }
        ]

    # LangGraph State Machine Trace 모사
    execution_plan = {
        "framework": "LangGraph (StateGraph v0.2)",
        "graph_nodes": [
            {"node": "intake_parser", "status": "completed", "duration_ms": 42},
            {"node": "metric_correlator", "status": "completed", "duration_ms": 88},
            {"node": "rag_knowledge_synthesis", "status": "completed", "duration_ms": 115},
            {"node": "risk_gatekeeper", "status": "completed", "duration_ms": 35},
        ],
        "state_transitions": [
            "START -> intake_parser -> metric_correlator -> rag_knowledge_synthesis -> risk_gatekeeper -> END"
        ],
        "confidence_score": 0.94,
    }

    return DeepAgentAnalyzeResponse(
        analysis_id=analysis_id,
        root_cause_hypothesis=root_cause,
        confidence_score=0.94,
        risk_level=risk_level,
        requires_human_approval=requires_approval,
        sla_response_limit_minutes=sla_limit,
        recommended_actions=actions,
        execution_plan=execution_plan,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )
