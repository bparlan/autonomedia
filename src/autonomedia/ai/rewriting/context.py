from dataclasses import dataclass, field


@dataclass
class RewriteContext:
    source_idea: str
    tags: list[str] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)
    url: str | None = None
    platform: str = "general"

    def to_prompt_block(self) -> str:
        """Serializes the context into a structured prompt block."""
        lines = [
            "--- CONTEXT ---",
            f"Platform: {self.platform}",
            f"Idea: {self.source_idea}",
            f"Tags: {', '.join(self.tags)}",
            f"Mentions: {', '.join(self.mentions)}",
        ]
        if self.url:
            lines.append(f"URL: {self.url}")
        lines.append("--- END CONTEXT ---")
        return "\n".join(lines)
