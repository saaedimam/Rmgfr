from __future__ import annotations
import asyncpg
from datetime import datetime, timedelta, timezone

class RuleResult:
    __slots__ = ("score","reasons","outcome")
    def __init__(self, score:int, reasons:list[str], outcome:str):
        self.score = score
        self.reasons = reasons
        self.outcome = outcome  # allow|review|deny

async def evaluate_rules(conn: asyncpg.Connection, project_id: str, event_id: str) -> RuleResult:
    # fetch event & config
    ev = await conn.fetchrow("select id, actor_user_id, ip, device_hash, event_ts from events where id=$1 and project_id=$2", event_id, project_id)
    if not ev:
        raise ValueError("event not found")
    cfg = await conn.fetchrow(
        "select max_events_per_ip,max_events_per_user,max_events_per_device,max_events_global,window_seconds from rule_configs where project_id=$1",
        project_id
    )
    # defaults if no config yet
    C = {
        "ip": (cfg["max_events_per_ip"] if cfg else 60),
        "user": (cfg["max_events_per_user"] if cfg else 60),
        "device": (cfg["max_events_per_device"] if cfg else 120),
        "global": (cfg["max_events_global"] if cfg else 5000),
        "win": (cfg["window_seconds"] if cfg else 300),
    }
    win_start = ev["event_ts"] - timedelta(seconds=C["win"])
    reasons = []
    score = 0

    # counts within window (project-scoped)
    cnt_global = await conn.fetchval("select count(*) from events where project_id=$1 and event_ts >= $2", project_id, win_start)
    if cnt_global > C["global"]:
        reasons.append("global_velocity")
        score += 50

    if ev["ip"]:
        cnt_ip = await conn.fetchval("select count(*) from events where project_id=$1 and ip=$2 and event_ts >= $3", project_id, ev["ip"], win_start)
        if cnt_ip > C["ip"]:
            reasons.append("ip_velocity")
            score += 30

    if ev["actor_user_id"]:
        cnt_user = await conn.fetchval("select count(*) from events where project_id=$1 and actor_user_id=$2 and event_ts >= $3", project_id, ev["actor_user_id"], win_start)
        if cnt_user > C["user"]:
            reasons.append("user_velocity")
            score += 25

    if ev["device_hash"]:
        cnt_dev = await conn.fetchval("select count(*) from events where project_id=$1 and device_hash=$2 and event_ts >= $3", project_id, ev["device_hash"], win_start)
        if cnt_dev > C["device"]:
            reasons.append("device_velocity")
            score += 20

    # simple mapping to outcome
    outcome = "allow"
    if score >= 60: outcome = "deny"
    elif score >= 25: outcome = "review"
    return RuleResult(score, reasons, outcome)
