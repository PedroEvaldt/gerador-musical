import re
from dataclasses import dataclass


_INITIAL_DELAY_PATTERN = re.compile(r"^\[(\d+)]\s*(.*)$", re.DOTALL)


@dataclass(frozen=True, slots=True)
class ParsedVoiceLine:
    initial_delay_beats: int
    body: str


class InitialDelayParser:
    def parse(self, line: str) -> ParsedVoiceLine:
        if not line.startswith("["):
            return ParsedVoiceLine(initial_delay_beats=0, body=line)

        match = _INITIAL_DELAY_PATTERN.match(line)
        if not match:
            raise ValueError(
                "Invalid initial delay. Use [n] at the beginning of the line, "
                "where n is a non-negative integer."
            )

        return ParsedVoiceLine(
            initial_delay_beats=int(match.group(1)),
            body=match.group(2),
        )
