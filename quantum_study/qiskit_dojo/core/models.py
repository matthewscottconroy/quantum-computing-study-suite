"""Domain models for qiskit-dojo."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Kata:
    id: str
    section: str
    title: str
    difficulty: str            # "beginner" | "intermediate" | "advanced"
    prompt: str                # task statement (markdown-ish plain text)
    starter_code: str
    test_code: str
    solution_code: str
    hints: list[str] = field(default_factory=list)


@dataclass
class DojoConfig:
    sections: list[str]
    kata_count: int
    shuffle: bool = True       # False = curriculum order (by section)


@dataclass
class RunResult:
    passed: bool
    output: str                # combined stdout + stderr from the harness
    phase: str = ""            # "pass" | "user_error" | "test_failed" | "timeout" | "crash"
    duration_secs: float = 0.0


@dataclass
class KataAttempt:
    kata: Kata
    passed: bool = False
    tries: int = 0
    hints_used: int = 0
    revealed_solution: bool = False


@dataclass
class SessionStats:
    attempts: list[KataAttempt] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.attempts)

    @property
    def passed(self) -> int:
        return sum(1 for a in self.attempts if a.passed)

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0
