# ==============================================================================
# 사내 Mock Enterprise API 컨테이너 빌드용 Dockerfile (Python 3.11-slim)
# ==============================================================================
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

WORKDIR /app

# 필수 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY main.py /app/

# 포트 노출
EXPOSE 8000

# FastAPI 서버 구동
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
