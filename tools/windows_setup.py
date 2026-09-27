#!/usr/bin/env python3
"""
Windows setup for the notes system (the Mac equivalents are notes_schedule.sh / whatsapp_bridge.sh).

Usage (PowerShell, from the repo root):
  python tools\\windows_setup.py check            # what's installed (read-only)
  python tools\\windows_setup.py env              # write .env (asks for the Notion token, hidden)
  python tools\\windows_setup.py schedule         # Task Scheduler: Sunday 10:00 review + hourly Notion sync
  python tools\\windows_setup.py unschedule
  python tools\\windows_setup.py bridge-install   # WhatsApp bridge (read-only) — optional, see workflow
  python tools\\windows_setup.py bridge-link      # first run: scan the QR
  python tools\\windows_setup.py bridge-start     # start now + at every login (hidden)
  python tools\\windows_setup.py bridge-stop
  python tools\\windows_setup.py status
  Add --dry-run to print the commands instead of running them.
"""
import argparse
import getpass
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOGS = ROOT / ".tmp" / "notes_rag" / "logs"
TASK_FOLDER = "Notas"

BRIDGE_REPO = "https://github.com/lharries/whatsapp-mcp.git"
BRIDGE_COMMIT = "7d6a06d"                      # reviewed 2026-09-27 (same as whatsapp_bridge.sh)
BRIDGE_DIR = Path(os.environ.get("WHATSAPP_BRIDGE_HOME", Path.home() / "whatsapp-mcp"))
REST_CALL = "\tstartRESTServer(client, messageStore, 8080)"
REST_OFF = "\t// startRESTServer disabled: read-only bridge (no /api/send). Patched by tools/windows_setup.py"
MSYS_GCC = Path(r"C:\msys64\ucrt64\bin")
STARTUP = Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"

DRY = False


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd))
    if DRY:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(cmd, **kw)


def ask(q):
    return input(f"{q} [s/N] ").strip().lower() in ("s", "si", "sí", "y", "yes")


def pythonw():
    """pythonw.exe next to the current interpreter: runs without opening a console window."""
    exe = Path(sys.executable)
    w = exe.with_name("pythonw.exe")
    return w if w.exists() else exe


# ── .env ───────────────────────────────────────────────────────────────────────

def write_env(path, values):
    """Merge values into .env, ASCII/UTF-8 without BOM (a BOM breaks the first key for python-dotenv)."""
    lines = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
    keep = [l for l in lines if l.split("=", 1)[0] not in values]
    keep += [f"{k}={v}" for k, v in values.items()]
    path.write_text("\n".join(keep) + "\n", encoding="utf-8")


def cmd_env():
    token = getpass.getpass("  Token de Notion (ntn_..., no se muestra): ").strip()
    if not token.startswith(("ntn_", "secret_")):
        sys.exit("  ✗ Eso no parece un token de Notion.")
    write_env(ROOT / ".env", {"NOTION_TOKEN": token, "NOTION_PENDIENTES_DB": "0987fdfa4c0c47e9ad1517b5dd945528"})
    print("  ✓ .env escrito. Probá: python tools\\notion_sync.py --dry-run")


# ── Scheduling ─────────────────────────────────────────────────────────────────

def task_commands():
    """schtasks /Create commands: pythonw + run_logged, so no window pops up and errors land in a log."""
    runner = ROOT / "tools" / "run_logged.py"

    def tr(script):
        return f'"{pythonw()}" "{runner}" "{ROOT / "tools" / script}"'

    return [
        ["schtasks", "/Create", "/F", "/TN", rf"{TASK_FOLDER}\Revision semanal",
         "/TR", tr("weekly_review.py"), "/SC", "WEEKLY", "/D", "SUN", "/ST", "10:00"],
        ["schtasks", "/Create", "/F", "/TN", rf"{TASK_FOLDER}\Sync Notion",
         "/TR", tr("notion_sync.py"), "/SC", "HOURLY", "/MO", "1"],
    ]


def cmd_schedule():
    LOGS.mkdir(parents=True, exist_ok=True)
    cmds = task_commands()
    env = (ROOT / ".env").read_text(encoding="utf-8-sig") if (ROOT / ".env").exists() else ""
    if "NOTION_TOKEN=" not in env:
        print("  – Sin NOTION_TOKEN en .env: programo solo la revisión semanal.")
        cmds = cmds[:1]
    for c in cmds:
        run(c, check=True)
    print(f"  ✓ Programado. Ver: Programador de tareas → Biblioteca → {TASK_FOLDER}. Logs: {LOGS}")


def cmd_unschedule():
    for name in ("Revision semanal", "Sync Notion"):
        run(["schtasks", "/Delete", "/F", "/TN", rf"{TASK_FOLDER}\{name}"])


# ── WhatsApp bridge ────────────────────────────────────────────────────────────

def patch_bridge_source(src):
    """Disable the bridge's unauthenticated REST server (/api/send on every interface)."""
    src = src.replace("\r\n", "\n")
    if REST_OFF in src:
        return src
    if src.count(REST_CALL + "\n") != 1:
        raise RuntimeError("No encontré la llamada a startRESTServer: el código del bridge cambió, no compilo.")
    return src.replace(REST_CALL + "\n", REST_OFF + "\n")


def bridge_exe():
    return BRIDGE_DIR / "whatsapp-bridge" / "whatsapp-bridge.exe"


def cmd_bridge_install():
    print("  ⚠ Se vincula como 'dispositivo vinculado' con una librería no oficial: WhatsApp puede desconectarlo\n"
          "    o restringir la cuenta. La base local guarda TODOS tus chats (el sistema lee solo Psi/Ide/Vida).")
    if not DRY and not ask("¿Seguir?"):
        return
    missing = [p for p in ("git", "go") if not shutil.which(p)]
    if missing or not (MSYS_GCC / "gcc.exe").exists():
        print("  Falta instalar (una vez):")
        if "git" in missing:
            print("    winget install -e --id Git.Git")
        if "go" in missing:
            print("    winget install -e --id GoLang.Go")
        if not (MSYS_GCC / "gcc.exe").exists():
            print("    winget install -e --id MSYS2.MSYS2")
            print('    C:\\msys64\\usr\\bin\\bash.exe -lc "pacman -S --noconfirm mingw-w64-ucrt-x86_64-gcc"')
        print("  Cerrá y abrí PowerShell, y volvé a correr bridge-install.")
        if not DRY:
            return
    if not (BRIDGE_DIR / ".git").exists():
        run(["git", "clone", "-q", BRIDGE_REPO, str(BRIDGE_DIR)], check=True)
    run(["git", "-C", str(BRIDGE_DIR), "fetch", "-q", "origin"], check=True)
    run(["git", "-C", str(BRIDGE_DIR), "checkout", "-q", BRIDGE_COMMIT], check=True)
    main_go = BRIDGE_DIR / "whatsapp-bridge" / "main.go"
    if not DRY:
        main_go.write_text(patch_bridge_source(main_go.read_text(encoding="utf-8")), encoding="utf-8")
    env = {**os.environ, "CGO_ENABLED": "1", "PATH": f"{MSYS_GCC};{os.environ.get('PATH', '')}"}
    run(["go", "build", "-o", "whatsapp-bridge.exe", "."], cwd=BRIDGE_DIR / "whatsapp-bridge", env=env, check=True)
    print(f"  ✓ Compilado sin servidor REST: {bridge_exe()}\n  Siguiente: python tools\\windows_setup.py bridge-link")


def cmd_bridge_link():
    print("  Escaneá el QR: WhatsApp → Dispositivos vinculados → Vincular dispositivo.\n"
          "  Cuando termine de sincronizar, Ctrl+C y corré bridge-start.")
    run([str(bridge_exe())], cwd=bridge_exe().parent)


def startup_vbs():
    """Hidden launcher in the Startup folder: runs the bridge at every login without a window."""
    log = bridge_exe().parent / "store" / "bridge.log"
    cmd = f'cmd /c cd /d ""{bridge_exe().parent}"" && ""{bridge_exe()}"" >> ""{log}"" 2>&1'
    return f'CreateObject("WScript.Shell").Run "{cmd}", 0, False\n'


def cmd_bridge_start():
    (bridge_exe().parent / "store").mkdir(parents=True, exist_ok=True)
    vbs = STARTUP / "notas-whatsapp-bridge.vbs"
    print(f"  → {vbs}")
    if not DRY:
        vbs.write_text(startup_vbs(), encoding="utf-8")
    run(["wscript.exe", str(vbs)])
    print("  ✓ Corriendo oculto y arranca solo al iniciar sesión. Log: store\\bridge.log")


def cmd_bridge_stop():
    run(["taskkill", "/F", "/IM", "whatsapp-bridge.exe"])
    vbs = STARTUP / "notas-whatsapp-bridge.vbs"
    if vbs.exists() and not DRY:
        vbs.unlink()
    print("  ✓ Parado y sacado del inicio. Sacá también el dispositivo en WhatsApp → Dispositivos vinculados.")


# ── Status ─────────────────────────────────────────────────────────────────────

def cmd_check():
    print(f"  Python   {sys.version.split()[0]}  ({sys.executable})")
    for tool in ("git", "go", "claude"):
        print(f"  {tool:<8} {'✓' if shutil.which(tool) else '— no instalado'}")
    print(f"  gcc      {'✓' if (MSYS_GCC / 'gcc.exe').exists() else '— no (solo hace falta para el bridge)'}")
    for mod in ("requests", "dotenv"):
        try:
            __import__(mod)
            print(f"  {mod:<8} ✓")
        except ImportError:
            print(f"  {mod:<8} — falta: python -m pip install -r requirements.txt")
    env = (ROOT / ".env").read_text(encoding="utf-8-sig") if (ROOT / ".env").exists() else ""
    print(f"  .env     {'✓ NOTION_TOKEN' if 'NOTION_TOKEN=' in env else '— sin NOTION_TOKEN (corré: env)'}")


def cmd_status():
    cmd_check()
    run(["schtasks", "/Query", "/TN", rf"{TASK_FOLDER}\Revision semanal"])
    running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq whatsapp-bridge.exe"], capture_output=True,
                             text=True).stdout if not DRY else ""
    print(f"  bridge   {'corriendo' if 'whatsapp-bridge.exe' in running else 'parado'}")


COMMANDS = {"check": cmd_check, "env": cmd_env, "schedule": cmd_schedule, "unschedule": cmd_unschedule,
            "bridge-install": cmd_bridge_install, "bridge-link": cmd_bridge_link,
            "bridge-start": cmd_bridge_start, "bridge-stop": cmd_bridge_stop, "status": cmd_status}


def main():
    global DRY
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=COMMANDS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    DRY = args.dry_run
    if os.name != "nt" and not DRY:
        sys.exit("Esto es para Windows (en Mac: notes_schedule.sh / whatsapp_bridge.sh). Probá con --dry-run.")
    COMMANDS[args.cmd]()


if __name__ == "__main__":
    main()
