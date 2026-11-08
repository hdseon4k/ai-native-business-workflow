# n8n 기반 On-Premise sLM & Agentic Orchestration 분석 및 교육 설계 검토 보고서

본 문서는 **n8n의 Sustainable Use License** 하에서 **온프레미스 LLM/sLM**을 연동하여 **Advanced AI & Agentic Orchestration 기반의 AI Native Business Workflow 교육 과정**을 개설하는 방안에 대한 기술적·법적 타당성 분석 및 대체 기술 검토 결과를 정리한 문서입니다.

---

## 1. 검토 배경 및 목표

- **교육 목표**: 데이터 주권 및 망분리 환경을 요구하는 기업 고객을 대상으로, 오픈소스/온프레미스 기반의 AI Native 비즈니스 워크플로우 구축 및 에이전틱 오케스트레이션 실무 역량 배양.
- **주요 검토 항목**:
  1. n8n의 Sustainable Use License(공정 코드) 하에서 교육/실습 운영의 적합성
  2. 온프레미스 소형 언어 모델(sLM)의 Tool Calling 및 Agent 루프 수행 가능성
  3. 경쟁 기술(Dify, Flowise, LangGraph 등)과의 비교 우위 및 진보도 평가
  4. 프로덕션 레벨 교육을 위한 최적 아키텍처 및 권장 기술 스택

---

## 2. n8n 개요 및 핵심 정체성

n8n은 분산된 시스템, API, DB를 시각적으로 연결하는 **소스 공개형(Source-available) 워크플로우 자동화 도구**입니다.

- **Self-hosting & Data Sovereignty**: 사내 인프라(Docker, Kubernetes)에 배포하여 데이터 외부 유출 없이 내부망에서만 워크플로우 처리 가능.
- **Node-based Canvas**: 400여 개 이상의 통합 노드 및 범용 HTTP Request, Webhook, Cron 트리거 제공.
- **Code Flexibility**: 단계별 `Code Node`를 통해 JavaScript(Node.js) 및 Python 스크립트 실행 지원.
- **Advanced AI Integration**: LangChain 네이티브 노드(Agent, Memory, Tool, Vector Store, Embeddings)를 기본 탑재하여 시각적 에이전트 구축 지원.

---

## 3. 라이선스(Sustainable Use License) 적합성 검토

### 3.1 핵심 규정
n8n의 Sustainable Use License는 내부 업무용(Internal Use) 셀프 호스팅을 무료로 보장하지만, **"n8n의 소프트웨어 기능을 제3자에게 호스팅/매니지드 서비스(SaaS 형태)로 제공하여 상업적 경쟁을 유발하는 행위"**를 엄격히 금지합니다.

### 3.2 교육 시나리오별 법적 적합성 판정

| 실습 환경 구성 방식 | 적합성 | 상세 설명 및 유의사항 |
| :--- | :---: | :--- |
| **수강생 로컬/개인 VM 설치** | **완전 적합** | 수강생 PC(Docker Desktop) 또는 각자에게 할당된 개별 VM에 n8n을 직접 띄워 실습하는 형태는 라이선스 위반 소지가 없음. |
| **1인 1컨테이너 자동 프로비저닝** | **적합** | 교육 플랫폼에서 수강생마다 독립된 격리 샌드박스 컨테이너를 일시 배포하고 세션 종료 후 파기하는 실습실 형태. |
| **기관 단일 n8n 멀티테넌트 제공** | **위험/주의** | 기관이 단일 대규모 n8n 인스턴스를 호스팅하고 유료 수강생들에게 계정/워크스페이스 형태로 접근 권한을 판매하는 경우 라이선스 침해 해석 가능성 존재. |

> [!TIP]
> **권장 배포 방식**: 수강생용 `docker-compose.yml`(n8n + Ollama + Qdrant) 템플릿을 제공하여 개인 환경 또는 독립 인스턴스에서 구동하도록 설계합니다.

---

## 4. 기술적 실현 가능성 (On-Premise LLM/sLM 연동)

### 4.1 연동 아키텍처
- **Ollama Node**: n8n에 기본 내장된 `Ollama Model` 노드를 통해 별도 코딩 없이 로컬 엔드포인트(`http://localhost:11434`)와 직결.
- **OpenAI Compatible Node**: 고속 서빙 엔진인 `vLLM`, `TGI`, `LocalAI`를 연동할 경우 `OpenAI Chat Model` 노드에서 Base URL만 교체하여 활용 가능.

### 4.2 sLM의 에이전틱 수행 역량 (Tool Calling & JSON Schema)
과거 7B 미만 모델은 ReAct 루프에서 JSON 파싱 실패나 무한 호출 오류가 잦았으나, 최근 세대의 모델은 고도화된 Function Calling 튜닝을 지원합니다.

- **권장 sLM 스택**:
  - **Qwen 2.5 (7B / 14B / 32B-Instruct)**: 도구 호출 정확도, JSON 스키마 준수율, 한국어 처리 능력 모두 현존 sLM 중 최상위.
  - **Llama 3.1 / 3.2 (8B-Instruct)**: 뛰어난 지시 이행 능력 및 Tool Calling 안정성.
  - **Mistral-Nemo (12B-Instruct)**: 정밀한 추론 및 확장 컨텍스트(128k) 지원.
- **하드웨어 요구사항**:
  - **8B (Q4_K_M 양자화)**: VRAM 8~12GB (RTX 3060/4060 또는 Mac M-시리즈 16GB RAM) 수준에서 20~40 tokens/s로 원활한 실습 가능.
  - **14B~32B**: VRAM 16~24GB (RTX 3090/4090) 권장.

---

## 5. 대체 기술 비교 및 프레임워크 진보도 평가

```
                    [비즈니스 시스템 통합 중심]
                                ▲
                                │   n8n
                                │
[시각적 No-Code/Low-Code] ──────┼────── [코드 기반 Code-First]
                                │   Dify
        Flowise / Langflow      │
                                │   LangGraph / CrewAI
                                ▼
                      [순수 AI/Agent 제어 중심]
```

### 프레임워크별 심층 비교

| 비교 항목 | **n8n** | **Dify** | **Flowise / Langflow** | **LangGraph / CrewAI** |
| :--- | :--- | :--- | :--- | :--- |
| **정체성** | 엔터프라이즈 시스템 통합 자동화 | AI Native 앱/RAG 파이프라인 플랫폼 | LangChain 시각적 UI 래퍼 | 코드 기반 복합 상태 머신 에이전트 |
| **엔터프라이즈 I/O** | **최상** (400+ 커넥터, Webhook, DB) | 보통 (HTTP 도구 위주) | 취약 (AI 전용 노드 위주) | 직접 코드로 구현 필요 |
| **RAG/AI 정밀 제어** | 보통 (LangChain 기본 노드 수준) | **최상** (하이브리드 검색, 리랭킹, 청킹) | 양호 (다양한 VectorStore 지원) | **최상** (자유도 무제한) |
| **에이전트 오케스트레이션** | ReAct 기반 단일/서브워크플로우 | 워크플로우 + 멀티 에이전트 | 단일 체인/ReAct 위주 | **최상** (순환 그래프, HITL, 분기) |
| **교육 진입 장벽** | **낮음** (비개발자~엔지니어 수용) | **낮음** (직관적 GUI) | 낮음 | **높음** (Python 숙련 필수) |

---

## 6. 교육적 가치 및 시장성 분석

1. **차별화된 포지셔닝**:
   - 단순 "Chatbot 만들기"나 "프롬프트 작성법"이 아닌, **ERP/DB/메신저와 AI가 유기적으로 맞물리는 "End-to-End 비즈니스 자동화"**를 다룸.
2. **망분리/보안 기업 수요 독점**:
   - OpenAI, Claude API 사용이 원천 금지된 금융, 공공, 대기업 제조 R&D 환경에서 즉시 적용 가능한 **On-Premise Full-Stack** 실습 커리큘럼 확보.
3. **학습 곡선 최적화**:
   - 복잡한 비동기 코드 작성 없이 시각적 캔버스에서 Agent의 Thought/Action/Observation 루프를 데이터 페이로드 단위로 추적 가능하여 교육 효과 극대화.

---

## 7. CLO 권장 하이브리드 커리큘럼 아키텍처

비즈니스 시스템과의 유연한 결합과 AI 추론의 정밀성을 동시에 확보하기 위해 **"n8n (Integration Backbone) + Ollama/sLM (Agent Core)"**의 하이브리드 파이프라인 구성을 권장합니다.

```
[External Trigger]
  - 사내 메일 인입 / Slack 멘션 / Webhook / DB 변경 감지
         │
         ▼
[n8n: Pre-processing & Context Gathering]
  - 데이터 정제, 사내 레거시 DB 조회, 첨부파일 추출
         │
         ▼
[Ollama / Local sLM: Agentic Decision Loop]
  - Qwen 2.5 (7B/14B)가 사용자 의도 분석
  - 필요 시 n8n의 서브 워크플로우(Custom Tool) 호출 (ex: ERP 재고 확인)
  - 최종 답변 및 실행 계획 도출
         │
         ▼
[n8n: Action Execution & Logging]
  - Jira 티켓 발행 / 이메일 회신 / Slack 알림 / 감사 로그 DB 적재
```

### 추천 실습 환경 패키징 (Docker Compose 스택)
- **Workflow Engine**: `n8n` (Node.js 기반, Sustainable Use License)
- **Local Model Serving**: `Ollama` (Qwen 2.5 7B-Instruct)
- **Vector Database**: `Qdrant` 또는 `pgvector`
- **Embedding Model**: `bge-m3` 또는 `nomic-embed-text`

