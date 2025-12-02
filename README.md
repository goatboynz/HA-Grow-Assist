<p align="center">
  <img src="https://raw.githubusercontent.com/goatboynz/HA-Grow-Assist/main/images/logo.svg" alt="Grow Room Manager Logo" width="400">
</p>

<h1 align="center">Grow Room Manager</h1>

<p align="center">
  <strong>Home Assistant integration for managing cannabis flowering rooms using the Athena Pro Line methodology</strong>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS"></a>
  <a href="https://github.com/goatboynz/HA-Grow-Assist/releases"><img src="https://img.shields.io/github/release/goatboynz/HA-Grow-Assist.svg" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/goatboynz/HA-Grow-Assist.svg" alt="License"></a>
</p>

---

## ✨ Features

- 🏠 **Multi-Room Support** - Manage F1, F2, F3+ flowering rooms
- 📅 **Auto Task Generation** - 35 tasks automatically created when you add a room
- 📊 **Smart Sensors** - Track day, phase, EC, dryback, environmental targets
- 📝 **Grow Journaling** - Save notes and camera snapshots
- 🔔 **Automation Blueprints** - Ready-to-use notifications
- 📤 **Export Logs** - Export journal to CSV or JSON

## 🚀 Quick Start

### 1. Install via HACS

[![Open HACS Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=goatboynz&repository=HA-Grow-Assist&category=integration)

Or manually: HACS → Custom repositories → Add `https://github.com/goatboynz/HA-Grow-Assist`

### 2. Add a Room

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Grow Room Manager"**
3. Enter:
   - Room ID (e.g., `f1`)
   - Room Name (e.g., `Flower Room 1`)
   - Start Date (Day 1 of flower)
   - Calendar entity (optional)
   - Todo list entity (optional)
4. Click **Submit** → Tasks auto-generate!

### 3. Add Dashboard Cards

Copy cards from `lovelace/cards/` or use the full dashboard from `lovelace/grow_room_dashboard.yaml`

**That's it! No configuration.yaml changes needed.**

---

## 📊 Sensors Created

Each room creates 4 sensors:

| Sensor | Description |
|--------|-------------|
| `sensor.{room}_grow_status` | Current day, phase, EC, dryback, environmental targets |
| `sensor.{room}_grow_progress` | Percentage through 84-day cycle |
| `sensor.{room}_next_task` | Next scheduled task with days until |
| `sensor.{room}_journal_entries` | Journal entry count |

---

## 🛠️ Services

| Service | Description |
|---------|-------------|
| `grow_room_manager.generate_tasks` | Generate 35 calendar/todo tasks |
| `grow_room_manager.add_journal_entry` | Add note with optional photo |
| `grow_room_manager.set_start_date` | Update room start date |
| `grow_room_manager.export_journal` | Export to CSV or JSON |
| `grow_room_manager.get_today_tasks` | Fire event for today's tasks |

---

## 📅 Athena Pro Line Schedule

### Phase Overview

| Phase | Days | EC | Dryback | Key Actions |
|-------|------|-----|---------|-------------|
| **Stretch** | 1-21 | 3.0 | 20-25% | Defoliation Day 2, IPM sprays |
| **Bulk** | 22-55 | 3.0 | 30-40% | Maintenance every 3 days |
| **Finish** | 56-84 | 1.5 | 40-50% | Fade nutrients, harvest prep |

### Critical Days

- **Day 2**: Heavy defoliation (strip lower 1/3)
- **Day 21**: Final defoliation + LAST IPM spray
- **Day 42**: Major maintenance prune
- **Day 56**: Switch to Athena Fade (zero nitrogen)
- **Day 77-84**: Harvest window

### Environmental Targets

| Phase | Day Temp | Night Temp | Humidity | VPD |
|-------|----------|------------|----------|-----|
| Stretch | 78-82°F | 68-72°F | 55-65% | 1.0-1.2 |
| Bulk | 78-82°F | 65-70°F | 50-60% | 1.2-1.4 |
| Finish | 75-78°F | 62-68°F | 40-50% | 1.4-1.6 |

---

## 🎨 Dashboard Cards

Pre-built cards available in `lovelace/cards/`:

- `room_status_card.yaml` - Full room status display
- `all_rooms_overview.yaml` - All rooms at a glance
- `environmental_targets_card.yaml` - Temp, humidity, VPD targets
- `next_task_card.yaml` - Upcoming task details
- `journal_card.yaml` - Journal entries and quick add
- `generate_tasks_card.yaml` - Task generation buttons

---

## 🔔 Automation Blueprints

Copy `blueprints/` folder to your config for:

- **Daily Task Notification** - Morning alerts for scheduled tasks
- **Phase Change Notification** - Alert on phase transitions
- **Harvest Window Alert** - Notification when harvest window opens

---

## 📁 File Storage

| Type | Location |
|------|----------|
| Journal entries | `/config/grow_logs/{room_id}.json` |
| Snapshots | `/config/www/grow_logs/{room_id}/` |
| Exports | `/config/www/grow_logs/` |

---

## 🐛 Troubleshooting

Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.grow_room_manager: debug
```

---

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Credits

Based on the **Athena Pro Line** cultivation methodology.

---

<p align="center">
  <img src="https://raw.githubusercontent.com/goatboynz/HA-Grow-Assist/main/images/icon.svg" alt="Icon" width="64">
</p>
