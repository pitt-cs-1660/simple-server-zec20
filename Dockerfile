FROM python:3.12 AS builder
WORKDIR /app
RUN echo "Cloud Computing Simple Server" > README.md
COPY pyproject.toml ./
COPY cc_simple_server ./cc_simple_server
COPY tests ./tests
RUN pip install --no-cache-dir uv && \
    uv venv .venv && . .venv/bin/activate && uv sync --no-dev

FROM python:3.12-slim AS final
RUN useradd -m appuser
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/cc_simple_server ./cc_simple_server
COPY --from=builder /app/tests ./tests
EXPOSE 8000
CMD ["uvicorn", "cc_simple_server.server:app", "--host", "0.0.0.0", "--port", "8000"]