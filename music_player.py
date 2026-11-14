"""
CREATIVIA // Background Music Player
=====================================
Plays mp3 files using mpg123 in a background thread so Pyxel's
main loop is never blocked.  Falls back silently if mpg123 is absent.
"""

from __future__ import annotations
import os
import subprocess
import threading
import shutil
import time

_PLAYER_CMD = shutil.which("mpg123") or shutil.which("ffplay")

class MusicPlayer:
    """
    Cycles through a playlist of mp3 paths, looping indefinitely.
    Provides play / stop / next controls.
    """

    def __init__(self, tracks: list[str]) -> None:
        self._tracks   = [t for t in tracks if os.path.isfile(t)]
        self._index    = 0
        self._proc: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None
        self._running  = False
        self._lock     = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────────
    def start(self) -> None:
        if not self._tracks or not _PLAYER_CMD:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._kill_proc()

    def next_track(self) -> None:
        with self._lock:
            self._index = (self._index + 1) % max(1, len(self._tracks))
        self._kill_proc()   # loop thread will start the new track immediately

    def current_track_index(self) -> int:
        return self._index

    # ── Internal ──────────────────────────────────────────────────────────────
    def _loop(self) -> None:
        while self._running and self._tracks:
            with self._lock:
                path = self._tracks[self._index]

            try:
                if "mpg123" in _PLAYER_CMD:
                    cmd = [_PLAYER_CMD, "-q", path]
                else:
                    # ffplay: -nodisp suppresses video window, -autoexit stops when done
                    cmd = [_PLAYER_CMD, "-nodisp", "-autoexit", "-loglevel", "quiet", path]

                with self._lock:
                    self._proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                self._proc.wait()
            except Exception:
                time.sleep(1.0)
                continue

            if self._running:
                with self._lock:
                    self._index = (self._index + 1) % len(self._tracks)

    def _kill_proc(self) -> None:
        with self._lock:
            proc = self._proc
            self._proc = None
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
