FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false && poetry install --only main --no-root
COPY src ./src
ENV PYTHONPATH=/app/src
CMD ["python", "-m", "uvicorn", "travel_operations.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
