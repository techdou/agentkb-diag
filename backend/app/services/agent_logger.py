"""
Agent action logger that writes structured log entries in Markdown format.
Appends to workspace/wiki/log.md so every agent action is traceable.
"""

from datetime import datetime
from pathlib import Path


class AgentLogger:
    """Append-only structured logger for the agent pipeline.

    Each log entry records the round, agent role, action description,
    and an optional detail string. Output is valid Markdown suitable
    for rendering in the wiki UI.
    """

    def __init__(self, log_path: str = "workspace/wiki/log.md"):
        # Resolve relative to the project root (two levels up from this file).
        service_dir = Path(__file__).resolve().parent  # app/services/
        app_dir = service_dir.parent                    # app/
        backend_dir = app_dir.parent                    # backend/
        project_root = backend_dir.parent               # agentkb-diag/
        self.log_path = project_root / log_path
        self._ensure_path()

    def _ensure_path(self) -> None:
        """Create parent directories and log file if they do not exist."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("# Agent Pipeline Log\n\n", encoding="utf-8")

    def log(self, round_num: int, agent_name: str, action: str, detail: str = "") -> None:
        """Append a structured log entry.

        Args:
            round_num: Which experiment round this action belongs to.
            agent_name: Name of the agent role (e.g. "Summary Agent").
            action: Brief description of what happened.
            detail: Optional extra detail (e.g. token counts, concept list).
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"[{timestamp}] [ROUND {round_num}] [{agent_name}] {action}"
        if detail:
            entry += f" — {detail}"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{entry}\n")

    def get_recent(self, n: int = 20) -> list[str]:
        """Return the last *n* log lines."""
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
        # Skip the header line if present
        if lines and lines[0].startswith("#"):
            lines = lines[1:]
        return [l for l in lines[-n:] if l.strip()]
