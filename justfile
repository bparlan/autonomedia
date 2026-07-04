# === Fast feedback loop ===
check:
    @uv run ruff check --select E,W,F,I,ASYNC .

fix:
    @uv run ruff check --fix --select E,W,F,I,ASYNC .
    @uv run ruff format .

# === Pre-push ===
lint:
    @uv run ruff check .
    @uv run mypy .

# === Tests ===
test: test-code

test-code:
    @uv run pytest && uv run ruff check . && uv run mypy .