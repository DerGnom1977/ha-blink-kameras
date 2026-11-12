"""Blink-Kameras: Fachlogik (Port der Automationen aus blink_kameras.yaml)."""
from __future__ import annotations

import asyncio
import logging
from datetime import time as dtime

from homeassistant.core import Event

from .const import DOMAIN
from .framework import LogicBase, in_window, now_local

_LOGGER = logging.getLogger(__name__)

CAMS = {
    "flur": {"ort": "Flur", "key": "flur", "push": "blink_push_flur", "aktion": "blink_aktion_flur", "datei": "flur"},
    "buero": {"ort": "Büro", "key": "buero", "push": "blink_push_buero", "aktion": "blink_aktion_buero", "datei": "buero"},
}


class Logic(LogicBase):
    def __init__(self, rt) -> None:
        super().__init__(rt)
        self._busy: set[str] = set()
        rt.actions["reset"] = self._reset

    async def _reset(self) -> None:
        self.rt.reset_defaults()

    async def async_start(self) -> None:
        rt = self.rt
        for cam in CAMS:
            rt.track_state([rt.cfg(f"{cam}_motion")], self._make_motion_cb(cam))
        rt.track_state([rt.cfg("modus_entity")], self._modus_changed)

    # -- Bedingungen --------------------------------------------------------
    def _ruhe_ok(self) -> bool:
        rt = self.rt
        if not rt.on("blink_ruhezeit_aktiv"):
            return True
        von: dtime = rt.get("blink_ruhe_von")
        bis: dtime = rt.get("blink_ruhe_bis")
        return not in_window(now_local().time().replace(microsecond=0), von, bis)

    def _wann_ok(self) -> bool:
        rt = self.rt
        w = rt.get("blink_wann")
        m = rt.state(rt.cfg("modus_entity"))
        return w == "Immer" or (w == "Nur wenn niemand da" and m == "Niemand da") or (
            w == "Nur wenn jemand da" and m == "Zuhause"
        )

    def _kein_doppelpush(self) -> bool:
        """Anwesenheit schickt bereits einen Push, wenn niemand da ist."""
        rt = self.rt
        return not (
            rt.is_state(rt.cfg("modus_entity"), "Niemand da")
            and rt.is_state(rt.cfg("anw_kamera_push"), "on")
            and rt.is_state(rt.cfg("anw_kamera_weitere"), "on")
        )

    # -- Bewegung -----------------------------------------------------------
    def _make_motion_cb(self, cam: str):
        async def _cb(event: Event) -> None:
            new = event.data.get("new_state")
            if new is None or new.state != "on":
                return
            if cam in self._busy:
                return
            rt = self.rt
            c = CAMS[cam]
            if not rt.on(c["push"]) or rt.get(c["aktion"]) == "Nichts":
                return
            if not (self._ruhe_ok() and self._wann_ok() and self._kein_doppelpush()):
                return
            self._busy.add(cam)
            rt.spawn(self._handle(cam))

        return _cb

    async def _handle(self, cam: str) -> None:
        rt = self.rt
        c = CAMS[cam]
        kamera = rt.cfg(f"{cam}_camera")
        try:
            if rt.on("blink_frisches_bild"):
                await rt.call("blink", "trigger_camera", {"entity_id": kamera})
                await asyncio.sleep(6)
            data = {
                "entity_id": kamera,
                "tag": f"blink_{c['key']}",
                "url": f"/{self.rt.cfg('dashboard_path') or 'dashboard-blink'}",
                "push": {"interruption-level": "active"},
            }
            await rt.notify(f"🎥 Blink: {c['ort']}", "Bewegung erkannt.", data)
            if rt.get(c["aktion"]) == "Push + Clip speichern":
                await asyncio.sleep(30)
                stamp = now_local().strftime("%Y%m%d_%H%M%S")
                ordner = str(rt.cfg("clip_dir")).rstrip("/")
                await rt.call(
                    "blink",
                    "save_video",
                    {"name": c["ort"], "filename": f"{ordner}/{c['datei']}_{stamp}.mp4"},
                )
            await asyncio.sleep(int(rt.flt("blink_pause", 5)) * 60)
        finally:
            self._busy.discard(cam)

    # -- Scharf/Unscharf ----------------------------------------------------
    async def _modus_changed(self, event: Event) -> None:
        rt = self.rt
        new = event.data.get("new_state")
        if new is None or not rt.on("blink_mit_anwesenheit"):
            return
        ziele = {"entity_id": [rt.cfg("flur_detect"), rt.cfg("buero_detect")]}
        if new.state == "Niemand da":
            await rt.call("switch", "turn_on", ziele)
        elif new.state == "Zuhause":
            await rt.call("switch", "turn_off", ziele)
