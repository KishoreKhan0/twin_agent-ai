# TwinAgent AI Docker image
#
# This image runs the existing local MVP inside a container.
# It is intentionally simple: one image can run either the API or dashboard,
# depending on the command supplied by docker-compose.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY configs ./configs
COPY docs ./docs
COPY knowledge_base ./knowledge_base
COPY scripts ./scripts
COPY src ./src
COPY tests ./tests

RUN mkdir -p data/raw data/generated data/processed data/incidents data/reports

ENV PYTHONPATH=/app/src

EXPOSE 8000
EXPOSE 8501

CMD ["python", "scripts/bootstrap_demo_data.py"]
