<p align="center">
  <img src="https://raw.githubusercontent.com/goatboynz/HA-Grow-Assist/main/images/logo.svg" alt="Grow Room Manager Logo" width="400">
</p>

<h1 align="center">Grow Room Manager</h1>

<p align="center">
  <strong>Home Assistant integration for managing cannabis grow rooms using the Athena Pro Line methodology</strong>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS"></a>
  <a href="https://github.com/goatboynz/HA-Grow-Assist/releases"><img src="https://img.shields.io/github/release/goatboynz/HA-Grow-Assist.svg" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/goatboynz/HA-Grow-Assist.svg" alt="License"></a>
</p>

---

## ✨ Features

- 🌸 **Flower Rooms** - 84-day cycle with 35 automated tasks
- 🌱 **Veg Rooms** - Track multiple batches (clones, mothers, veg plants)
- 📅 **Auto Task Generation** - Calendar/todo tasks created automatically
- 📊 **Smart Sensors** - Track day, phase, EC, dryback, environmental targets
- 📝 **Grow Journaling** - Save notes and camera snapshots
- 🔔 **Automation Blueprints** - Ready-to-use notifications
- 📤 **Export Logs** - Export journal to CSV or JSON
- 🧪 **Athena Feeding Calculator** - Nutrient recipes for all phases

## 🚀 Quick Start

### 1. Install via HACS

[![Open HACS Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=goatboynz&repository=HA-Grow-Assist&category=integration)

Or manually: HACS → Custom repositories → Add `https://github.com/goatboynz/HA-Grow-Assist`

### 2. Add a Room

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Grow Room Manager"**
3. Choose room type:
   - **Flower Room** - 84-day cycle with fixed start date
   - **Veg Room** - Continuous operation with batch tracking
4. Configure room settings
5. Click **Submit** → Tasks auto-generate!

**That's it! No configuration.yaml changes needed.**

### 3. Add the Dashboard

1. **Settings** → **Dashboards** → **Add Dashboard**
2. Name it "Grow Rooms"
3. Open the new dashboard, click **Edit** (pencil icon)
4. Click the 3 dots menu → **Raw configuration editor**
5. Delete everything and paste contents of `lovelace/grow_room_dashboard.yaml`
6. Save

The dashboard includes:
- **Overview** - All rooms at a glance
- **Veg** - Batch management with quick-add buttons
- **F1/F2/F3** - Individual flower room pages
- **Journal** - Quick notes for all rooms
- **Feeding** - Nutrient calculator
- **Settings** - Start dates and task generation
- **Guide** - Athena Pro Line reference

---

## 🌸 Flower Rooms

Flower rooms track a single 84-day cycle from flip to harvest.

### Sensors Created

| Sensor | Description |
|--------|-------------|
| `sensor.{room}_grow_status` | Current day, phase, EC, dryback, environmental targets |
| `sensor.{room}_grow_progress` | Percentage through 84-day cycle |
| `sensor.{room}_next_task` | Next scheduled task with days until |
| `sensor.{room}_journal_entries` | Journal entry count |

### Athena Pro Line Schedule

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

## 🌱 Veg Rooms

Veg rooms track multiple plant batches at different stages simultaneously.

### Veg Stages

| Stage | Duration | EC | Description |
|-------|----------|-----|-------------|
| **Clone** | ~14 days | 0.8 | Rooting in dome, high humidity |
| **Pre-Veg** | ~7 days | 1.2 | Post-transplant establishment |
| **Early Veg** | ~14 days | 1.8 | Rapid growth, training begins |
| **Late Veg** | ~14 days | 2.2 | Final growth, ready for flower |
| **Mother** | Ongoing | 2.0 | Maintained for cuttings |

### Sensors Created

| Sensor | Description |
|--------|-------------|
| `sensor.{room}_status` | Batch count, plants by stage, recommended EC |
| `sensor.{room}_active_batches` | Count and details of active batches |
| `sensor.{room}_next_task` | Next task across all batches |
| `sensor.{room}_journal_entries` | Journal entry count |

### Batch Workflow

1. **Add Batch**: Call `grow_room_manager.add_veg_batch` when clones arrive
2. **Update Stage**: Call `grow_room_manager.update_veg_batch` as plants progress
3. **Move to Flower**: Call `grow_room_manager.move_to_flower` when ready

### Example: Adding Clones

```yaml
service: grow_room_manager.add_veg_batch
data:
  room_id: veg
  batch_name: "OG Kush Dec 2024"
  start_date: "2024-12-01"
  stage: Clone
  plant_count: 24
  strain: "OG Kush"
  destination_room: f1
  notes: "Clones from mother #3"
```

### Example: Moving to Flower

```yaml
service: grow_room_manager.move_to_flower
data:
  room_id: veg
  batch_id: og_kush_dec_2024_20241201_120000
  flower_room_id: f1
  flower_start_date: "2024-12-15"
```

---

## 🧪 Athena Feeding Chart

### Flower Nutrients (per gallon)

| Phase | Core | Bloom | Fade | Cleanse | Target EC |
|-------|------|-------|------|---------|-----------|
| Stretch | 3g | 3g | - | - | 3.0 |
| Bulk | 3g | 3g | - | Optional | 3.0 |
| Finish | - | - | 3g | Optional | 1.5 |

### Veg Nutrients (per gallon)

| Stage | Core | Grow | Balance | pH Down | Target EC |
|-------|------|------|---------|---------|-----------|
| Clone | 1g | 1g | 0.5g | As needed | 0.8 |
| Pre-Veg | 1.5g | 1.5g | 0.5g | As needed | 1.2 |
| Early Veg | 2g | 2g | 1g | As needed | 1.8 |
| Late Veg | 2.5g | 2.5g | 1g | As needed | 2.2 |
| Mother | 2g | 2g | 1g | As needed | 2.0 |

**Note**: pH Down is used as needed to achieve target pH of 5.8-6.2. Balance provides additional calcium. Cleanse can be used weekly for salt buildup.

---

## 🛠️ Services

### Flower Room Services

| Service | Description |
|---------|-------------|
| `grow_room_manager.generate_tasks` | Generate 35 calendar/todo tasks |
| `grow_room_manager.set_start_date` | Update room start date |
| `grow_room_manager.get_today_tasks` | Fire event for today's tasks |

### Veg Room Services

| Service | Description |
|---------|-------------|
| `grow_room_manager.add_veg_batch` | Add a new batch of plants |
| `grow_room_manager.update_veg_batch` | Update batch stage/details |
| `grow_room_manager.move_to_flower` | Move batch to flower room |
| `grow_room_manager.list_veg_batches` | List all batches |

### Common Services

| Service | Description |
|---------|-------------|
| `grow_room_manager.add_journal_entry` | Add note with optional photo |
| `grow_room_manager.export_journal` | Export to CSV or JSON |
| `grow_room_manager.clear_tasks` | Clear tasks (manual) |

---

## 🎨 Dashboard & Cards

### Full Dashboard

A complete dashboard is available at `lovelace/grow_room_dashboard.yaml` with:
- Overview of all rooms
- Individual room pages (F1, F2, F3, Veg)
- Journal with quick-add buttons
- Feeding calculator
- Settings page
- Athena Pro Line guide

### Standalone Cards

Copy individual cards from `lovelace/cards/` to your own dashboards:

| Card | Description |
|------|-------------|
| `all_rooms_overview.yaml` | All rooms at a glance with progress gauges |
| `room_status_card.yaml` | Single flower room status |
| `veg_room_status_card.yaml` | Veg room with batch summary |
| `next_task_card.yaml` | Upcoming tasks for all rooms |
| `quick_journal_card.yaml` | Fast note entry buttons |
| `feeding_calculator_card.yaml` | Nutrient recipes |
| `journal_card.yaml` | Full journal interface |
| `veg_batch_manager_card.yaml` | Veg batch management |
| `generate_tasks_card.yaml` | Task generation buttons |

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
| Veg batches | `/config/grow_logs/{room_id}_batches.json` |
| Snapshots | `/config/www/grow_logs/{room_id}/` |
| Exports | `/config/www/grow_logs/` |

---

## 🔄 Events

The integration fires events for automations:

| Event | Description |
|-------|-------------|
| `grow_room_manager_task_today` | Task scheduled for today |
| `grow_room_manager_veg_batch_added` | New batch added |
| `grow_room_manager_veg_stage_changed` | Batch stage updated |
| `grow_room_manager_batch_moved_to_flower` | Batch moved to flower |
| `grow_room_manager_veg_batches_list` | Batch list response |

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
