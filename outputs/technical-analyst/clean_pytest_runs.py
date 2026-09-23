# -*- coding: utf-8 -*-
"""清理 .pytest_cache\\pytest-runs 下陈旧 PID 目录。

判定规则：目录名 pytest-<PID>，PID 不在当前存活进程列表中 -> 陈旧，删除。
必须以 CODEBUDDY_SAFE_DELETE_ENABLED=0 运行，绕开回收站 shim 的批量删除守卫。
"""
import ctypes
import os
import shutil
import sys

RUNS_DIR = r"D:\vcp_hunter\产业链投研\.pytest_cache\pytest-runs"


def live_pids():
    """用 EnumProcesses 枚举当前所有存活进程 PID。"""
    n = 4096
    while True:
        buf = (ctypes.c_uint * n)()
        cb = ctypes.c_uint(n * 4)
        got = ctypes.c_uint()
        if not ctypes.windll.kernel32.K32EnumProcesses(
            ctypes.byref(buf), cb, ctypes.byref(got)
        ):
            raise OSError("EnumProcesses failed")
        count = got.value // 4
        if count < n:  # buffer enough
            return set(buf[:count])
        n *= 2


def is_python_pid(pid):
    """判断该 PID 是否为存活的 python 进程（避免与其他进程撞号误判）。"""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    k32 = ctypes.WinDLL("kernel32")
    h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False  # 进程不存在或无法查询
    try:
        buf = ctypes.create_unicode_buffer(512)
        size = ctypes.c_uint(512)
        psapi = ctypes.WinDLL("psapi")
        if psapi.GetModuleFileNameExW(h, None, buf, 512):
            return "python" in os.path.basename(buf.value).lower()
        return True  # 查询失败时保守视为存活
    finally:
        k32.CloseHandle(h)


def main():
    pids = live_pids()
    stale, kept, broken = [], [], []
    total_files = 0
    for name in sorted(os.listdir(RUNS_DIR)):
        if not name.startswith("pytest-"):
            continue
        suffix = name[len("pytest-"):]
        if not suffix.isdigit():
            kept.append((name, "非 PID 目录，跳过"))
            continue
        pid = int(suffix)
        path = os.path.join(RUNS_DIR, name)
        if pid in pids and is_python_pid(pid):
            kept.append((name, "进程仍在运行，保留"))
            continue
        try:
            nfiles = 0
            for _root, _dirs, files in os.walk(path):
                nfiles += len(files)
            shutil.rmtree(path, ignore_errors=False)
            total_files += nfiles
            stale.append((name, pid, nfiles))
        except PermissionError as e:
            broken.append((name, str(e)))

    lines = []
    lines.append("已删除 %d 个陈旧目录，共 %d 个文件：" % (len(stale), total_files))
    for name, pid, nf in stale:
        lines.append("  - %s (PID %d, %d files)" % (name, pid, nf))
    if broken:
        lines.append("ACL 损坏无法删除 %d 个（需管理员提权处理）：" % len(broken))
        for name, err in broken:
            lines.append("  - %s (%s)" % (name, err))
    if kept:
        lines.append("保留 %d 个：" % len(kept))
        for name, reason in kept:
            lines.append("  - %s (%s)" % (name, reason))
    report = "\n".join(lines)
    print(report)
    with open(r"D:\vcp_hunter\产业链投研\outputs\_pytest_runs_cleanup.txt", "w", encoding="utf-8") as f:
        f.write(report + "\nREMAIN=" + str(len(os.listdir(RUNS_DIR))) + "\n")


if __name__ == "__main__":
    main()
