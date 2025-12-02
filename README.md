# Grow Room Manager for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/YOUR_USERNAME/grow_room_manager.svg)](https://github.com/YOUR_USERNAME/grow_room_manager/releases)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/grow_room_manager.svg)](LICENSE)

A HACS-compatible custom integration for managing medical cannabis flowering rooms using the **Athena Pro Line** cultivation methodology.

## Features

- **Multi-Room Support**: Manage multiple flowering rooms (F1, F2, F3, etc.)
- **Grow Journaling**: Save notes and camera snapshots with timestamps
- **Automated Crop Steering**: Auto-generate tasks based on the Athena Pro Line schedule
- **Calendar & Todo Integration**: Tasks appear in your Home Assistant calendar and todo lists
- **Status Sensors**: Track current day, phase, recommended EC, and dryback targets

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=YOUR_USERNAME&repository=grow_room_manager&category=integration)

**Or manually:**

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add: `https://github.com/YOUR_USERNAME/grow_room_manager`
4. Select category: **Integration**
5. Click **Add**
6. Search for "Grow Room Manager" and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/YOUR_USERNAME/grow_room_manager/releases)
2. Extract and copy the `custom_components/grow_room_manager` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

Add the following to your `configuration.yaml`:

```yaml
grow_room_manager:
  rooms:
    - room_id: f1
      name: "Flower Room 1"
      calendar_entity: calendar.grow_calendar
      todo_entity: todo.grow_tasks_f1
    - room_id: f2
      name: "Flower Room 2"
      calendar_entity: calendar.grow_calendar
      todo_entity: todo.grow_tasks_f2
    - room_id: f3
      name: "Flower Room 3"
      calendar_entity: calendar.grow_calendar
      todo_entity: todo.grow_tasks_f3

# Required helpers for each room
input_datetime:
  f1_start_date:
    name: "F1 Start Date"
    has_date: true
    has_time: false
  f2_start_date:
    name: "F2 Start Date"
    has_date: true
    has_time: false
  f3_start_date:
    name: "F3 Start Date"
    has_date: true
    has_time: false

input_text:
  f1_journal_note:
    name: "F1 Journal Note"
    max: 255
  f2_journal_note:
    name: "F2 Journal Note"
    max: 255
  f3_journal_note:
    name: "F3 Journal Note"
    max: 255
```

## Services

### `grow_room_manager.add_journal_entry`

Add a journal entry with optional camera snapshot.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `room_id` | Yes | Room identifier (e.g., "f1") |
| `note` | Yes | Journal note text |
| `image_entity` | No | Camera entity for snapshot |

### `grow_room_manager.generate_tasks`

Generate calendar events and todo items from the Athena schedule.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `room_id` | Yes | Room identifier |
| `start_date` | Yes | First day of flower (YYYY-MM-DD) |

### `grow_room_manager.clear_tasks`

Clear generated tasks for a room.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `room_id` | Yes | Room identifier |

## Athena Pro Line Schedule

The integration implements a comprehensive 84-day schedule with detailed task information:

### Phase 1: Stretch (Weeks 1-3, Days 1-21)
- **Day 1**: Flip day - begin 12/12 light cycle, set EC to 3.0
- **Day 2**: Heavy defoliation/strip (lollipop lower 1/3)
- **Days 3-21**: IPW spray applications (2x/week, 6 total)
- **Day 21**: Final defoliation (skirt up), STOP all IPW sprays

### Phase 2: Bulk (Weeks 4-8, Days 22-55)
- **Day 22**: Begin vegetative steering (30-40% dryback)
- **Every 3 days**: Maintenance checks for airflow & canopy management
- **Day 42**: Major defoliation day - ensure airflow through canopy
- Recurring tasks: Days 25, 28, 31, 34, 37, 40, 42, 43, 46, 49, 52, 55

### Phase 3: Finish (Weeks 8-12, Days 56-84)
- **Day 56**: Switch to Athena Fade (zero nitrogen), reduce EC to 1.5
- **Every 3 days**: Maintenance checks, trichome monitoring
- **Day 77**: Harvest window opens
- **Day 84**: End of cycle - harvest & sanitize lines with Athena Renew/Reset

Each task includes:
- Detailed action checklists
- Environmental targets (temp, humidity, VPD)
- Nutrient recommendations
- Expected plant status
- Source references to Athena Handbook

## Sensors

Each room gets a status sensor (`sensor.{room_id}_grow_status`) with:

- **State**: Current day (e.g., "Day 45")
- **Attributes**:
  - `phase`: Current phase (Stretch/Bulk/Finish)
  - `recommended_ec`: Target EC for current phase
  - `target_dryback`: Dryback percentage target
  - `days_remaining`: Days until harvest window
  - `harvest_window`: Boolean if in harvest window

## File Storage

- **Journal entries**: `/config/grow_logs/{room_id}.json`
- **Snapshots**: `/config/www/grow_logs/{room_id}/{timestamp}.jpg`
- **Snapshot URLs**: `/local/grow_logs/{room_id}/{timestamp}.jpg`

## Troubleshooting

Enable debug logging to diagnose issues:

```yaml
logger:
  default: info
  logs:
    custom_components.grow_room_manager: debug
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

Based on the Athena Pro Line cultivation methodology.

---

**Note:** Replace `YOUR_USERNAME` in this README with your actual GitHub username after creating the repository.
