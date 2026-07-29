<div align="center">

# 🔥 Fire & Gas Detection

### A Multi-Sensor Raspberry Pi Early-Warning Node — Camera + Flame Sensor + MQ-2 Gas, with Buzzer & Phone Alerts

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)
![CV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-00C896.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-eahmeddarwish-181717?logo=github)](https://github.com/eahmeddarwish/fire-gas-detection)
![Status](https://img.shields.io/badge/status-corrected%20%26%20verified-brightgreen)

**Built by [Ahmed Darwish](mailto:eahmeddarwish@gmail.com)**

[📖 Features](#-key-features--أهم-المميزات) · [🔌 Wiring](#-hardware--wiring--العتاد-والتوصيل) · [🚀 Quick Start](#-quick-start--البدء-السريع) · [⚠️ Honest Limitations](#-honest-limitations--محدوديات-صادقة) · [⭐ Star](https://github.com/eahmeddarwish/fire-gas-detection)

</div>

![Fire & Gas Detection](docs/fire-gas-detection.png)

---

## 🌍 Overview | نظرة عامة

**[English]**
An early-warning node that fuses **three independent signals** so a single false
reading doesn't trigger — and a single missed reading doesn't stay silent:

1. **Camera** — OpenCV HSV segmentation flags fire-coloured regions.
2. **IR flame sensor** — a GPIO interrupt catches direct flame instantly.
3. **MQ-2 gas sensor** — a GPIO digital output catches smoke / LPG / methane.

On a confirmed event it sounds a **buzzer** and pushes a **phone notification**
(Pushover). A cooldown stops alert spam. It runs on a **Raspberry Pi** with real
sensors, or on **any PC in simulation mode** (GPIO is mocked automatically) so
the camera pipeline can be demoed without hardware.

**[العربية]**
عقدةُ إنذارٍ مبكّر تدمج **ثلاث إشاراتٍ مستقلة** حتى لا تُطلق قراءةٌ خاطئةٌ واحدة
إنذارًا كاذبًا، ولا تمرّ قراءةٌ فائتةٌ بصمت:

1. **الكاميرا** — تجزئة HSV بـ OpenCV ترصد المناطق بلون النار.
2. **حسّاس اللهب IR** — مقاطعة GPIO تلتقط اللهب المباشر فورًا.
3. **حسّاس الغاز MQ-2** — خرج GPIO رقمي يلتقط الدخان/غاز البترول/الميثان.

عند تأكيد الحدث يُطلق **صفّارة** ويرسل **إشعارًا للهاتف** (Pushover)، مع فترة تهدئة
تمنع تكرار الإنذار. يعمل على **Raspberry Pi** بحسّاساتٍ حقيقية، أو على **أي حاسوب
في وضع المحاكاة** (يُحاكى GPIO تلقائيًا) لتجربة مسار الكاميرا بلا عتاد.

---

## ✨ Key Features | أهم المميزات

| Feature | Description |
|---|---|
| 🎥 **Vision detection** | HSV colour segmentation + pixel-count threshold for fire |
| 🔦 **Flame interrupt** | GPIO edge callback — reacts the instant flame appears |
| 🫧 **Gas sensing** | MQ-2 digital output for smoke / LPG / methane |
| 📲 **Phone alerts** | Pushover push notification with timestamp |
| 🔔 **Local siren** | Buzzer pattern on a dedicated GPIO pin |
| 🧊 **Cooldown** | Thread-safe minimum gap between alerts |
| 🖥️ **Simulation mode** | Auto-mocks GPIO off-Pi so it runs anywhere |

---

## 🔌 Hardware & Wiring | العتاد والتوصيل

| Component | Pi Pin (BCM) | Notes |
|---|---|---|
| Buzzer (+) | GPIO 16 | Through a transistor/resistor for anything but a tiny buzzer |
| IR flame sensor DO | GPIO 21 | Digital out; adjust the module's sensitivity pot |
| MQ-2 gas sensor DO | GPIO 20 | Digital out; needs ~24 h burn-in for stable readings |
| USB / Pi camera | — | `CAMERA_INDEX=0` by default |
| GND / 5V | — | Common ground shared by all modules |

Pins are configurable via environment variables (`BUZZER_PIN`, `FLAME_PIN`, `GAS_PIN`).

---

## 🚀 Quick Start | البدء السريع

```bash
pip install -r requirements.txt

# Optional: enable phone alerts (else alerts print to the console)
export PUSHOVER_TOKEN="Your Pushover App Token Here"
export PUSHOVER_USER="Your Pushover User Key Here"

# Simulation on a PC (GPIO mocked) OR real run on a Raspberry Pi — same command:
python fire_gas_detection.py     # press 'q' to quit
```

On a Pi, also install the GPIO library: `pip install RPi.GPIO`.

---

## 🧠 Technical Decisions | قرارات تقنية

- **Sensor fusion, not a single detector.** Camera + flame + gas cover each
  other's blind spots (colour false-positives vs. true flame vs. invisible smoke).
- **GPIO abstraction.** A mock GPIO is injected when `RPi.GPIO` is unavailable, so
  the exact same code runs on a laptop for development and on the Pi in production.
- **Env-var secrets.** Pushover credentials come from the environment; with none
  set, the app degrades gracefully to console logging instead of failing.
- **Thread-safe cooldown.** Alert state is guarded by a lock so concurrent
  camera/flame/gas events can't double-fire.

---

## ⚠️ Honest Limitations | محدوديات صادقة

**[English]**
- **Colour-based vision is naive.** Sunlight, red clothing, or warm lamps can trip
  the HSV mask; the threshold is a starting point, not a tuned classifier.
- **Digital gas/flame outputs only.** Uses the sensors' DO pins (on/off), not
  analog concentration — no ppm readings (the Pi has no ADC without extra hardware).
- **MQ-2 needs burn-in and calibration** for the physical environment.
- **Not a certified fire-safety device.** A learning / prototype project, not a
  replacement for a rated smoke/heat alarm.

**[العربية]**
- **الرؤية اللونية ساذجة.** أشعة الشمس أو الملابس الحمراء أو المصابيح الدافئة قد
  تُخدع قناع HSV؛ العتبة نقطة بداية لا مُصنِّفًا مضبوطًا.
- **خرج رقمي فقط للغاز/اللهب.** يستخدم أطراف DO (تشغيل/إيقاف) لا التركيز التماثلي —
  بلا قراءات ppm (لا يوجد ADC في الـ Pi بدون عتادٍ إضافي).
- **حسّاس MQ-2 يحتاج تسخينًا ومعايرة** لبيئة التشغيل الفعلية.
- **ليس جهاز سلامةٍ معتمَد.** مشروع تعلّم/نموذج أوّلي، لا بديل عن إنذار حريقٍ مُعتمَد.

---

## 🗺️ Roadmap | خطط التطوير

- [x] **Phase 1** — Camera + flame + gas fusion, buzzer + Pushover, simulation mode *(current)*
- [ ] **Phase 2** — Analog MQ-2 via an ADC (MCP3008) for real ppm thresholds
- [ ] **Phase 3** — Lightweight ML fire classifier to cut colour false-positives
- [ ] **Phase 4** — Local event log + optional MQTT to a home dashboard

---

## 👤 Author | المطور

<div align="center">

**Ahmed Darwish**

*Electrical & Computer Engineer | Python · Arduino · Raspberry Pi · AI/ML*

[![Email](https://img.shields.io/badge/Email-eahmeddarwish%40gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:eahmeddarwish@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-eahmeddarwish-181717?logo=github)](https://github.com/eahmeddarwish)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

⭐ **If this project is useful, please give it a star on GitHub!** ⭐

*Made with ❤️ by Ahmed Darwish*

</div>
