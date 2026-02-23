from __future__ import annotations

RULES = [
  ("tests", ["tests","test"]),
  ("api", ["api","controller","controllers","routes","router","http"]),
  ("domain", ["domain","model","models","entity","entities","core"]),
  ("service", ["service","services","use_case","use_cases","application"]),
  ("infra", ["infra","infrastructure","adapter","adapters","db","database","repository","repositories"]),
  ("utils", ["utils","common","shared","helpers","lib"]),
]

def detect_layer(rel_path: str) -> str:
    rp = rel_path.replace("\\","/").lower()
    parts = [p for p in rp.split("/") if p]
    for layer, cues in RULES:
        for cue in cues:
            if cue in parts:
                return layer
    return "unknown"
