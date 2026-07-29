"""
Fire & Gas Detection (Raspberry Pi)
===================================
A multi-sensor early-warning node that fuses three independent signals:

  1. Camera   -> OpenCV HSV colour segmentation flags fire-coloured regions.
  2. Flame    -> a digital IR flame sensor (GPIO interrupt) for direct flame.
  3. Gas      -> an MQ-2 smoke/gas sensor digital output (GPIO) for smoke/LPG.

On any confirmed event it sounds a buzzer and pushes a phone notification via
the Pushover API. A cooldown prevents alert spam.

Runs in two modes:
  * REAL HARDWARE  — on a Raspberry Pi with RPi.GPIO installed.
  * SIMULATION     — on any PC (GPIO is mocked automatically), so the camera
                     pipeline can be developed and demoed without a Pi.

Secrets (Pushover token/user) are read from environment variables — never
hard-coded. If they are unset, alerts are logged to the console instead.

Author : Ahmed Darwish  <eahmeddarwish@gmail.com>
License: MIT
"""

import os
import time
import threading
import http.client
import urllib.parse
from datetime import datetime

import cv2
import numpy as np

# --------------------------------------------------------------------------- #
# GPIO abstraction: use the real library on a Pi, otherwise a no-op mock so the
# rest of the program runs unchanged on a laptop (simulation mode).
# --------------------------------------------------------------------------- #
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except (ImportError, RuntimeError):
    ON_PI = False

    class _MockGPIO:
        BCM = OUT = IN = BOTH = HIGH = LOW = 0

        def setmode(self, *a):
            pass

        def setup(self, *a, **k):
            pass

        def output(self, *a):
            pass

        def add_event_detect(self, *a, **k):
            pass

        def add_event_callback(self, *a):
            pass

        def cleanup(self):
            pass

    GPIO = _MockGPIO()

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BUZZER_PIN = int(os.getenv("BUZZER_PIN", 16))
FLAME_PIN = int(os.getenv("FLAME_PIN", 21))
GAS_PIN = int(os.getenv("GAS_PIN", 20))          # MQ-2 digital output (DO)
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))

FIRE_PIXEL_THRESHOLD = 15000    # non-zero mask pixels that count as "fire"
COOLDOWN_SECONDS = 15           # minimum gap between alerts

PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")     # set in your environment
PUSHOVER_USER = os.getenv("PUSHOVER_USER")

# HSV colour band for fire-like regions (orange/red, bright).
LOWER_FIRE = np.array([0, 50, 50], dtype="uint8")
UPPER_FIRE = np.array([25, 255, 255], dtype="uint8")


class AlertManager:
    """Handles the buzzer, Pushover notifications, and cooldown state."""

    def __init__(self):
        self._last_alert = 0.0
        self._lock = threading.Lock()

    def can_alert(self):
        return time.time() - self._last_alert >= COOLDOWN_SECONDS

    def trigger(self, reason):
        """Fire an alert (buzzer + notification) if not in cooldown."""
        with self._lock:
            if not self.can_alert():
                return
            self._last_alert = time.time()
        threading.Thread(target=self._buzz, daemon=True).start()
        threading.Thread(target=self._notify, args=(reason,), daemon=True).start()

    @staticmethod
    def _buzz():
        for _ in range(4):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.6)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.1)

    @staticmethod
    def _notify(reason):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{reason} detected at {stamp}. Please call the authorities."
        if not (PUSHOVER_TOKEN and PUSHOVER_USER):
            print(f"[ALERT] {message}  (set PUSHOVER_TOKEN/PUSHOVER_USER to push)")
            return
        try:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request(
                "POST", "/1/messages.json",
                urllib.parse.urlencode({
                    "token": PUSHOVER_TOKEN,
                    "user": PUSHOVER_USER,
                    "message": message,
                }),
                {"Content-type": "application/x-www-form-urlencoded"},
            )
            resp = conn.getresponse()
            print(f"[Pushover] {resp.status} {resp.reason}")
            conn.close()
        except Exception as exc:
            print(f"[Pushover error] {exc}")


def setup_gpio(alerts):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(FLAME_PIN, GPIO.IN)
    GPIO.setup(GAS_PIN, GPIO.IN)
    if ON_PI:
        GPIO.add_event_detect(FLAME_PIN, GPIO.BOTH, bouncetime=300)
        GPIO.add_event_callback(FLAME_PIN, lambda ch: alerts.trigger("Flame"))
        GPIO.add_event_detect(GAS_PIN, GPIO.BOTH, bouncetime=300)
        GPIO.add_event_callback(GAS_PIN, lambda ch: alerts.trigger("Smoke/Gas"))


def detect_fire(frame):
    """Return (mask, fire_pixel_count) for the fire-coloured regions in a frame."""
    blur = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_FIRE, UPPER_FIRE)
    return mask, cv2.countNonZero(mask)


def main():
    alerts = AlertManager()
    setup_gpio(alerts)

    mode = "REAL HARDWARE" if ON_PI else "SIMULATION (GPIO mocked)"
    print(f"Fire & Gas Detection running in {mode}. Press 'q' to quit.")

    video = cv2.VideoCapture(CAMERA_INDEX)
    try:
        while True:
            grabbed, frame = video.read()
            if not grabbed:
                print("No camera frame — check CAMERA_INDEX.")
                break

            frame = cv2.resize(frame, (960, 540))
            mask, fire_pixels = detect_fire(frame)
            overlay = cv2.bitwise_and(frame, frame, mask=mask)

            if fire_pixels > FIRE_PIXEL_THRESHOLD:
                alerts.trigger("Fire (camera)")
                cv2.putText(frame, "FIRE!", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            cv2.imshow("camera", frame)
            cv2.imshow("fire-mask", overlay)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        video.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()
        print("Shut down cleanly.")


if __name__ == "__main__":
    main()
