# Convenience commands for the minimal system

default:
	@echo "Run 'just help' for available commands"

help:
	@echo "Available commands:"
	@echo "  just init-db     # Initialize database tables"
	@echo "  just create-idea TOPIC CONTENT "PLATFORMS"    # Create a new idea"
	@echo "  just approve ID PLATFORM [true|false]    # Approve an idea for a platform"
	@echo "  just post-one-shot ID "PLATFORMS"    # Post idea once to platforms"
	@echo "  just run-scheduler   # Start the background scheduler (runs forever)"
	@echo "  just test-one-shot  # Run integration tests"

init-db:
	@uv run python -c "import asyncio; from src.autonomedia.core.database import init_db; asyncio.run(init_db())"

create-idea:
	@if [ $$(echo "$" | wc -w) -lt 2 ]; then echo "Usage: just create-idea <topic> <content> [platforms...]"; exit 1; fi
	@TOPIC=$$(echo "$" | sed -n '1p');
	@CONTENT=$$(echo "$" | sed -n '2p');
	@PLATS=$$(shift 2; echo "$")
	@if [ -z "$$PLATS" ]; then PLATS="mastodon linkedin x"; fi
	@uv run python -c "
import asyncio, json
from src.autonomedia.core.database import store_idea
async def f():
    await store_idea($$TOPIC, $$CONTENT, json.loads($$PLATS))
asyncio.run(f())
" "$$(echo """{json.dumps("$$TOPIC")}"...")
approve:
	@if [ -z "$" ]; then echo "Usage: just approve <idea-id> <platform> [true|false]"; exit 1; fi
	@ID=$$(echo "$" | sed -n '1p');
	@PLATFORM=$$(echo "$" | sed -n '2p');
	@VERIFIED=$$(echo "$" | sed -n '3p')
	@if [ -z "$$VERIFIED" ]; then VERIFIED=true; fi
	@uv run python -c "
import asyncio
from src.autonomedia.core.database import set_verification
async def f():
    await set_verification($$ID, $$PLATFORM, $$VERIFIED == 'true')
asyncio.run(f())
"

post-one-shot:
	@if [ -z "$" ]; then echo "Usage: just post-one-shot <idea-id> [platforms...]"; exit 1; fi
	@ID=$$(echo "$" | sed -n '1p')
	@PLATS=$$(shift 1; echo "$")
	@if [ -z "$$PLATS" ]; then PLATS="mastodon linkedin x"; fi
	@uv run python -m src.autonomedia.run_manual --idea-id $$ID --platforms $$PLATS

run-scheduler:
	@uv run python -m src.autonomedia.scheduler

test-one-shot:
	@uv run pytest src/autonomedia/tests/test_one_shot.py -v
