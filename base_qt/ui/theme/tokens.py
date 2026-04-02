from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UiTokens:
    xs: int = 4
    s: int = 8
    m: int = 12
    l: int = 16
    xl: int = 24

    r_s: int = 6
    r_m: int = 10
    r_l: int = 14

    control_h: int = 30
    border_w: int = 1


TOKENS = UiTokens()


def as_qss_replacements(tokens: UiTokens = TOKENS) -> dict[str, str]:
    return {k: str(v) for k, v in tokens.__dict__.items()}
