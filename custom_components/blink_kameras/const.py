"""Blink-Kameras: Spezifikation."""
from __future__ import annotations

from .framework import Field, Spec

DOMAIN = "blink_kameras"
TITLE = "Blink Kameras"
PREFIX = "blink"
VERSION = "1.0.0"
DESCRIPTION = "Bewegungsmeldung, Ruhezeit und Scharfschaltung für Blink-Kameras (Flur, Büro)."
DASHBOARD_PATH = "dashboard-blink"

AKTIONEN = ["Nur Push", "Push + Clip speichern", "Nichts"]
WANN = ["Immer", "Nur wenn niemand da", "Nur wenn jemand da"]

FIELDS = [
    Field("notify_person1", "mobile_app_mein_handy", "text", "Notify-Dienst Person 1"),
    Field("notify_person2", "mobile_app_partner_handy", "text", "Notify-Dienst Person 2"),
    Field("flur_motion", "binary_sensor.flur_bewegung", "entity", "Flur: Bewegungssensor", ("binary_sensor",)),
    Field("flur_camera", "camera.flur", "entity", "Flur: Kamera", ("camera",)),
    Field("flur_detect", "switch.flur_bewegungserkennung", "entity", "Flur: Schalter Bewegungserkennung", ("switch",)),
    Field("buero_motion", "binary_sensor.buero_bewegung", "entity", "Büro: Bewegungssensor", ("binary_sensor",)),
    Field("buero_camera", "camera.buero", "entity", "Büro: Kamera", ("camera",)),
    Field("buero_detect", "switch.buero_bewegungserkennung", "entity", "Büro: Schalter Bewegungserkennung", ("switch",)),
    Field("modus_entity", "select.anwesenheit_modus", "entity", "Anwesenheits-Modus (Integration Anwesenheit)", ("select", "input_select")),
    Field("anw_kamera_push", "switch.anwesenheit_kamera_push", "entity", "Anwesenheit: Kamera-Push", ("switch", "input_boolean")),
    Field("anw_kamera_weitere", "switch.anwesenheit_kamera_weitere", "entity", "Anwesenheit: weitere Kameras", ("switch", "input_boolean")),
    Field("clip_dir", "/config/www/blink", "text", "Ordner für gespeicherte Clips"),
]

SPECS = [
    Spec("switch", "blink_push_flur", "Flur: bei Bewegung melden", "mdi:cctv", True),
    Spec("switch", "blink_push_buero", "Büro: bei Bewegung melden", "mdi:cctv", True),
    Spec("select", "blink_aktion_flur", "Flur: bei Bewegung", "mdi:motion-sensor", options=AKTIONEN, default="Nur Push"),
    Spec("select", "blink_aktion_buero", "Büro: bei Bewegung", "mdi:motion-sensor", options=AKTIONEN, default="Nur Push"),
    Spec("switch", "blink_frisches_bild", "Vor dem Push neues Bild holen", "mdi:camera-retake", True),
    Spec("select", "blink_wann", "Push senden", "mdi:account-clock", options=WANN, default="Nur wenn niemand da"),
    Spec("number", "blink_pause", "Pause zwischen Meldungen", "mdi:timer-sand", 5, 1, 60, 1, "min", "slider"),
    Spec("switch", "blink_ruhezeit_aktiv", "Ruhezeit (kein Push)", "mdi:sleep", False),
    Spec("time", "blink_ruhe_von", "Ruhezeit von", "mdi:weather-night", "22:00"),
    Spec("time", "blink_ruhe_bis", "Ruhezeit bis", "mdi:weather-sunset-up", "06:00"),
    Spec("switch", "blink_mit_anwesenheit", "Kameras mit „Ich gehe / Ich bin da“ ein-/ausschalten", "mdi:shield-home", False),
    Spec("switch", "blink_ziel_person1", "Push an Person 1", "mdi:cellphone-message", True),
    Spec("switch", "blink_ziel_person2", "Push an Person 2", "mdi:cellphone-message", True),
    Spec("button", "blink_standardwerte", "Standardwerte setzen", "mdi:restore", press="reset"),
]

SECTIONS = [
    ("Kameras", ["blink_push_flur", "blink_aktion_flur", "blink_push_buero", "blink_aktion_buero"]),
    ("Meldungen", ["blink_frisches_bild", "blink_wann", "blink_pause", "blink_ziel_person1", "blink_ziel_person2"]),
    ("Ruhezeit", ["blink_ruhezeit_aktiv", "blink_ruhe_von", "blink_ruhe_bis"]),
    ("Anwesenheit", ["blink_mit_anwesenheit"]),
    ("Werkzeuge", ["blink_standardwerte"]),
]
