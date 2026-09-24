# -*- coding: utf-8 -*-
"""
WorkBuddy 多账号共享历史对话脚本（非官方，本机使用）

原理：WorkBuddy 的会话列表按登录账号（user_id）过滤本地 workbuddy.db 的
sessions 表。本脚本把所有会话的 user_id 统一改成“当前登录账号”，
实现各账号看到同一份历史列表。

用法（在 WorkBuddy 对话里直接说“同步会话归属”即可，或手动执行）：
    python workbuddy_share_sessions.py           # 自动检测当前登录账号
    python workbuddy_share_sessions.py --uid <uuid>  # 手动指定目标账号

每次运行前自动备份数据库到 ~/.workbuddy/automation-backups/share_sessions_<时间戳>/
"""
import argparse
import datetime
import os
import re
import shutil
import sqlite3
import sys

BASE = os.path.expanduser(r"~\.workbuddy")
DB = os.path.join(BASE, "workbuddy.db")
LS_DIR = os.path.join(BASE, "local_storage")
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def detect_current_uid() -> str | None:
    """当前登录账号检测：storage/ 下按账号建的 user-<uid>[-personal] 目录，
    最近被写入的即当前账号。这些目录名只含真实账号 id，不会混入
    设备/工作区等其他 uuid。"""
    st = os.path.join(BASE, "storage")
    if not os.path.isdir(st):
        return None
    best = None  # (mtime, uid)
    for name in os.listdir(st):
        m = re.fullmatch(r"user-(" + UUID_RE.pattern + r")(-personal)?", name)
        if not m or not os.path.isdir(os.path.join(st, name)):
            continue
        uid = m.group(1)
        p = os.path.join(st, name)
        try:
            mtime = max(
                os.path.getmtime(os.path.join(p, x)) for x in os.listdir(p)
            ) if os.listdir(p) else os.path.getmtime(p)
        except OSError:
            continue
        # personal 目录优先级更高（同 uid 时加一个微小加权）
        weight = 1 if name.endswith("-personal") else 0
        key = (mtime + weight, uid)
        if best is None or key > best:
            best = key
    return best[1] if best else None


def backup_db() -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = os.path.join(BASE, "automation-backups", f"share_sessions_{stamp}")
    os.makedirs(bdir, exist_ok=True)
    for f in ("workbuddy.db", "workbuddy.db-wal", "workbuddy.db-shm"):
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(bdir, f))
    return bdir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uid", help="目标账号 user_id（默认自动检测当前登录账号）")
    args = ap.parse_args()

    if not os.path.exists(DB):
        print("[错误] 未找到数据库:", DB)
        return 1

    target = args.uid or detect_current_uid()
    if not target:
        print("[错误] 无法检测当前登录账号，请用 --uid 手动指定")
        return 1
    if not os.path.isdir(os.path.join(BASE, "storage", f"user-{target}")):
        print(f"[拒绝] {target} 不是本机已知的账号（storage/user-{target} 不存在），"
              "为防误迁到设备/工作区 ID，已中止。")
        return 1

    con = sqlite3.connect(DB, timeout=15)
    cur = con.cursor()
    before = dict(cur.execute(
        "select user_id, count(*) from sessions group by user_id"))
    if not before:
        print("没有任何会话，无需迁移")
        con.close()
        return 0
    if set(before) == {target}:
        print(f"[跳过] 全部 {sum(before.values())} 条会话已归属当前账号 {target}")
        con.close()
        return 0

    bdir = backup_db()
    cur.execute("update sessions set user_id=? where user_id<>?", (target, target))
    moved = cur.rowcount
    con.commit()

    after = dict(cur.execute(
        "select user_id, count(*) from sessions group by user_id"))
    con.close()

    print(f"[完成] 已把 {moved} 条会话迁移到当前账号 {target}")
    print(f"       迁移前分布: {before}")
    print(f"       迁移后分布: {after}")
    print(f"       数据库备份: {bdir}")
    print("[提示] 需完全退出并重启 WorkBuddy 后，会话列表才会刷新。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
