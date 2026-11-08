# AI Native Business Workflow 웹 교재 홈

> **환영합니다!** 본 웹북은 오픈소스 워크플로우 엔진 **n8n**과 온프레미스 **sLM(Ollama)**을 활용하여 엔터프라이즈 폐쇄망 환경의 **AI Native 비즈니스 오케스트레이션 파이프라인**을 처음부터 끝까지 혼자 구축해 볼 수 있도록 설계된 **5주(15시간) 자기주도학습 전자책**입니다.

---

## 🚀 학습 시작 방법

1. **우측 코드 복사 버튼(`[Copy]`) 활용**: 교안 내 모든 `curl` 명령어, System Prompt, JSON Schema, n8n 표현식(`{{ $json... }}`) 블록 우측 상단의 복사 버튼을 클릭하면 오타 없이 즉시 실습에 붙여넣을 수 있습니다.
2. **좌측 사이드바 목차 이동**: **Week 01**부터 **Week 05**까지 순서대로 진행하며, 막히는 부분이 생기면 GitHub 저장소의 `03_workflows/` 폴더에 있는 완성본 JSON 파일을 n8n으로 Import하여 비교해 보십시오.

---

## 📚 5주 커리큘럼 로드맵

| 주차 | 학습 모듈 | 핵심 실습 산출물 |
| :---: | :--- | :--- |
| **Week 01** | [온프레미스 인프라 구축 & 비정형 데이터 정형화](./Week01_Infra_and_Structured_Output.md) | Docker 5종 스택 구동 + JSON Schema 기반 장애 티켓 추출 및 DB 적재 |
| **Week 02** | [온프레미스 RAG 파이프라인 & 사내 지식 베이스](./Week02_OnPremise_RAG_Vector_Pipeline.md) | `bge-m3` 임베딩 + `Qdrant` 벡터 DB 인덱싱 및 환각 억제 Grounded QA |
| **Week 03** | [에이전틱 오케스트레이션 & 멀티 툴 바인딩](./Week03_Agentic_Orchestration_MultiTool.md) | ReAct 에이전트 + DB 조회 서브 워크플로우 + 실시간 서버 메트릭 API 연동 |
| **Week 04** | [프로덕션 신뢰성 엔지니어링 & Human-in-the-Loop](./Week04_Production_HITL_Fault_Tolerance.md) | 프롬프트 인젝션 가드레일 + `Auto-fixing Parser` + `Wait` 비동기 웹 승인 |
| **Week 05** | [하이브리드 아키텍처 확장 & End-to-End 캡스톤](./Week05_Hybrid_Capstone_and_LLMOps.md) | FastAPI/LangGraph 외부 추론 연동 + 4대 시나리오 엔드투엔드 자가 검증 |
