FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 启用字节码编译，加快启动速度
# enable compile bytecode to speedup startup
ENV UV_COMPILE_BYTECODE=1
# only install dependency, no need install the project itself(if it's a library)
# for app, we need to install the project
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

# copy source code
COPY . .

# if needed, install project itself
RUN uv sync --frozen --no-dev


# run env
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY src ./src

CMD ["python", "-m", "my_package"]
