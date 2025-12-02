/**
 * Grow Room Manager - Full Application Panel
 * Standalone UI accessible from Home Assistant sidebar
 */

class GrowRoomPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._currentView = 'overview';
    this._rooms = {};
    this._vegBatches = [];
    this._journal = {};
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialize();
      this._initialized = true;
    }
    this._loadData();
  }

  _initialize() {
    this.shadowRoot.innerHTML = `
      <style>${this._getStyles()}</style>
      <div class="app">
        <nav class="sidebar">
          <div class="logo">🌿 Grow Manager</div>
          <ul class="nav-menu">
            <li data-view="overview" class="active">📊 Overview</li>
            <li data-view="flower">🌸 Flower Rooms</li>
            <li data-view="veg">🌱 Veg Room</li>
            <li data-view="journal">📝 Journal</li>
            <li data-view="feeding">🧪 Feeding</li>
            <li data-view="settings">⚙️ Settings</li>
            <li data-view="guide">📖 Guide</li>
          </ul>
        </nav>
        <main class="content" id="main-content">
          <!-- Content loaded dynamically -->
        </main>
      </div>
    `;

    // Navigation click handlers
    this.shadowRoot.querySelectorAll('.nav-menu li').forEach(item => {
      item.addEventListener('click', (e) => {
        this.shadowRoot.querySelectorAll('.nav-menu li').forEach(i => i.classList.remove('active'));
        e.target.classList.add('active');
        this._currentView = e.target.dataset.view;
        this._renderView();
      });
    });

    this._renderView();
  }

  _getStyles() {
    return `
      :host {
        display: block;
        height: 100vh;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --bg-primary: #1a1a2e;
        --bg-secondary: #16213e;
        --bg-card: #0f3460;
        --accent: #e94560;
        --accent-green: #4ecca3;
        --text-primary: #eee;
        --text-secondary: #aaa;
      }
      .app {
        display: flex;
        height: 100%;
        background: var(--bg-primary);
        color: var(--text-primary);
      }
      .sidebar {
        width: 200px;
        background: var(--bg-secondary);
        padding: 20px 0;
        flex-shrink: 0;
      }
      .logo {
        font-size: 18px;
        font-weight: bold;
        padding: 0 20px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 10px;
      }
      .nav-menu {
        list-style: none;
        padding: 0;
        margin: 0;
      }
      .nav-menu li {
        padding: 12px 20px;
        cursor: pointer;
        transition: background 0.2s;
      }
      .nav-menu li:hover {
        background: rgba(255,255,255,0.1);
      }
      .nav-menu li.active {
        background: var(--accent);
        font-weight: 500;
      }
      .content {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
      }
      h1 { margin: 0 0 20px; font-size: 24px; }
      h2 { margin: 20px 0 10px; font-size: 18px; color: var(--accent-green); }
      .card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
      }
      .card-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
      }
      .stat {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      .stat:last-child { border-bottom: none; }
      .stat-label { color: var(--text-secondary); }
      .stat-value { font-weight: 500; }
      .progress-bar {
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
      }
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent-green), var(--accent));
        border-radius: 4px;
        transition: width 0.3s;
      }
      .btn {
        background: var(--accent);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        margin: 5px;
        transition: opacity 0.2s;
      }
      .btn:hover { opacity: 0.9; }
      .btn-secondary {
        background: var(--bg-secondary);
        border: 1px solid var(--accent);
      }
      .btn-success { background: var(--accent-green); }
      .input {
        background: var(--bg-secondary);
        border: 1px solid rgba(255,255,255,0.2);
        color: var(--text-primary);
        padding: 10px;
        border-radius: 6px;
        width: 100%;
        margin: 5px 0;
        box-sizing: border-box;
      }
      .input:focus {
        outline: none;
        border-color: var(--accent);
      }
      select.input {
        cursor: pointer;
      }
      .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
      }
      .badge-stretch { background: #f39c12; }
      .badge-bulk { background: #27ae60; }
      .badge-finish { background: #9b59b6; }
      .badge-clone { background: #3498db; }
      .badge-veg { background: #2ecc71; }
      .badge-mother { background: #e74c3c; }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      th { color: var(--text-secondary); font-weight: 500; }
      .journal-entry {
        background: var(--bg-secondary);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
      }
      .journal-date {
        color: var(--text-secondary);
        font-size: 12px;
        margin-bottom: 5px;
      }
      .quick-btns {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
      }
      .alert {
        background: rgba(233, 69, 96, 0.2);
        border: 1px solid var(--accent);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
      }
      .alert-success {
        background: rgba(78, 204, 163, 0.2);
        border-color: var(--accent-green);
      }
      .tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
      }
      .tab {
        padding: 10px 20px;
        background: var(--bg-secondary);
        border-radius: 6px;
        cursor: pointer;
      }
      .tab.active {
        background: var(--accent);
      }
    `;
  }


  async _loadData() {
    // Load rooms from HA states
    this._rooms = {
      f1: this._getRoomData('sensor.flower_room_1_grow_status', 'sensor.flower_room_1_grow_progress'),
      f2: this._getRoomData('sensor.flower_room_2_grow_status', 'sensor.flower_room_2_grow_progress'),
      f3: this._getRoomData('sensor.flower_room_3_grow_status', 'sensor.flower_room_3_grow_progress'),
    };
    
    // Load veg data
    const vegStatus = this._hass?.states['sensor.veg_room_status'];
    const vegBatches = this._hass?.states['sensor.veg_room_active_batches'];
    this._vegRoom = {
      status: vegStatus?.state || 'Not Configured',
      totalPlants: vegStatus?.attributes?.total_plants || 0,
      batchCount: vegBatches?.state || 0,
      batches: vegBatches?.attributes?.batches || [],
      batchesByStage: vegStatus?.attributes?.batches_by_stage || {},
      recommendedEc: vegStatus?.attributes?.recommended_ec || 1.5,
    };

    this._renderView();
  }

  _getRoomData(statusEntity, progressEntity) {
    const status = this._hass?.states[statusEntity];
    const progress = this._hass?.states[progressEntity];
    
    if (!status) {
      return { configured: false };
    }

    return {
      configured: true,
      status: status.state,
      day: status.attributes?.current_day,
      week: status.attributes?.current_week,
      phase: status.attributes?.phase || 'Unknown',
      ec: status.attributes?.recommended_ec,
      dryback: status.attributes?.target_dryback,
      daysRemaining: status.attributes?.days_remaining,
      progress: parseInt(progress?.state) || 0,
      startDate: status.attributes?.start_date,
      harvestWindow: status.attributes?.harvest_window,
      tempDay: status.attributes?.target_temp_day,
      tempNight: status.attributes?.target_temp_night,
      humidity: status.attributes?.target_humidity,
      vpd: status.attributes?.target_vpd,
    };
  }

  _renderView() {
    const content = this.shadowRoot.getElementById('main-content');
    if (!content) return;

    switch (this._currentView) {
      case 'overview':
        content.innerHTML = this._renderOverview();
        break;
      case 'flower':
        content.innerHTML = this._renderFlowerRooms();
        break;
      case 'veg':
        content.innerHTML = this._renderVegRoom();
        break;
      case 'journal':
        content.innerHTML = this._renderJournal();
        break;
      case 'feeding':
        content.innerHTML = this._renderFeeding();
        break;
      case 'settings':
        content.innerHTML = this._renderSettings();
        break;
      case 'guide':
        content.innerHTML = this._renderGuide();
        break;
    }

    this._attachEventListeners();
  }

  _renderOverview() {
    const rooms = ['f1', 'f2', 'f3'];
    
    return `
      <h1>📊 Overview</h1>
      
      <h2>🌸 Flower Rooms</h2>
      <div class="grid">
        ${rooms.map(id => this._renderRoomCard(id)).join('')}
      </div>

      <h2>🌱 Veg Room</h2>
      <div class="card">
        <div class="card-title">🌱 Veg Room</div>
        ${this._vegRoom.status === 'Not Configured' ? `
          <p>Veg room not configured. Add it via HA Settings → Devices & Services.</p>
        ` : `
          <div class="stat">
            <span class="stat-label">Status</span>
            <span class="stat-value">${this._vegRoom.status}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Active Batches</span>
            <span class="stat-value">${this._vegRoom.batchCount}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Total Plants</span>
            <span class="stat-value">${this._vegRoom.totalPlants}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Recommended EC</span>
            <span class="stat-value">${this._vegRoom.recommendedEc}</span>
          </div>
        `}
      </div>

      <h2>📋 Quick Actions</h2>
      <div class="quick-btns">
        <button class="btn" data-action="journal" data-room="f1">📝 F1 Note</button>
        <button class="btn" data-action="journal" data-room="f2">📝 F2 Note</button>
        <button class="btn" data-action="journal" data-room="f3">📝 F3 Note</button>
        <button class="btn btn-success" data-action="add-batch">🌱 Add Batch</button>
      </div>
    `;
  }

  _renderRoomCard(roomId) {
    const room = this._rooms[roomId];
    const name = roomId.toUpperCase();
    
    if (!room?.configured) {
      return `
        <div class="card">
          <div class="card-title">🌸 ${name}</div>
          <p style="color: var(--text-secondary)">Not configured</p>
          <p style="font-size: 12px">Add via HA Settings → Devices & Services</p>
        </div>
      `;
    }

    const phaseClass = room.phase?.toLowerCase() || '';
    
    return `
      <div class="card">
        <div class="card-title">
          🌸 ${name}
          <span class="badge badge-${phaseClass}">${room.phase}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Status</span>
          <span class="stat-value">${room.status}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${room.progress}%"></div>
        </div>
        <div class="stat">
          <span class="stat-label">Week</span>
          <span class="stat-value">${room.week || '-'}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Target EC</span>
          <span class="stat-value">${room.ec || '-'}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Days Remaining</span>
          <span class="stat-value">${room.daysRemaining ?? '-'}</span>
        </div>
        ${room.harvestWindow ? '<div class="alert alert-success">🎉 Harvest Window Open!</div>' : ''}
      </div>
    `;
  }


  _renderFlowerRooms() {
    return `
      <h1>🌸 Flower Rooms</h1>
      
      <div class="tabs">
        <div class="tab active" data-room="f1">F1</div>
        <div class="tab" data-room="f2">F2</div>
        <div class="tab" data-room="f3">F3</div>
      </div>

      <div id="flower-room-content">
        ${this._renderFlowerRoomDetail('f1')}
      </div>
    `;
  }

  _renderFlowerRoomDetail(roomId) {
    const room = this._rooms[roomId];
    const name = roomId.toUpperCase();

    if (!room?.configured) {
      return `
        <div class="card">
          <h2>${name} - Not Configured</h2>
          <p>Add this room via Home Assistant Settings → Devices & Services → Add Integration → Grow Room Manager</p>
        </div>
      `;
    }

    return `
      <div class="grid">
        <div class="card">
          <div class="card-title">📊 Status</div>
          <div class="stat">
            <span class="stat-label">Current Day</span>
            <span class="stat-value">${room.status}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Week</span>
            <span class="stat-value">${room.week || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Phase</span>
            <span class="stat-value"><span class="badge badge-${room.phase?.toLowerCase()}">${room.phase}</span></span>
          </div>
          <div class="stat">
            <span class="stat-label">Start Date</span>
            <span class="stat-value">${room.startDate || 'Not set'}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${room.progress}%"></div>
          </div>
          <div style="text-align: center; color: var(--text-secondary)">${room.progress}% Complete</div>
        </div>

        <div class="card">
          <div class="card-title">🎯 Targets</div>
          <div class="stat">
            <span class="stat-label">Target EC</span>
            <span class="stat-value">${room.ec || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Target Dryback</span>
            <span class="stat-value">${room.dryback || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Days to Harvest</span>
            <span class="stat-value">${room.daysRemaining ?? '-'}</span>
          </div>
        </div>

        <div class="card">
          <div class="card-title">🌡️ Environment</div>
          <div class="stat">
            <span class="stat-label">Day Temp</span>
            <span class="stat-value">${room.tempDay || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Night Temp</span>
            <span class="stat-value">${room.tempNight || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Humidity</span>
            <span class="stat-value">${room.humidity || '-'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">VPD</span>
            <span class="stat-value">${room.vpd || '-'}</span>
          </div>
        </div>
      </div>

      <h2>📝 Quick Journal</h2>
      <div class="card">
        <div class="quick-btns">
          <button class="btn" data-action="quick-note" data-room="${roomId}" data-note="All plants healthy">✅ All Good</button>
          <button class="btn" data-action="quick-note" data-room="${roomId}" data-note="Fed plants">💧 Fed</button>
          <button class="btn" data-action="quick-note" data-room="${roomId}" data-note="IPM spray completed">🐛 IPM</button>
          <button class="btn" data-action="quick-note" data-room="${roomId}" data-note="Defoliation completed">✂️ Pruned</button>
          <button class="btn" data-action="quick-note" data-room="${roomId}" data-note="EC/pH checked">📊 EC Check</button>
        </div>
        <input type="text" class="input" id="custom-note-${roomId}" placeholder="Custom note...">
        <button class="btn btn-secondary" data-action="custom-note" data-room="${roomId}">Add Custom Note</button>
      </div>

      <h2>⚙️ Actions</h2>
      <div class="card">
        <button class="btn" data-action="set-start-today" data-room="${roomId}">📅 Set Start to Today</button>
        <button class="btn btn-secondary" data-action="generate-tasks" data-room="${roomId}">📋 Generate Tasks</button>
        <button class="btn btn-secondary" data-action="export-journal" data-room="${roomId}">📤 Export Journal</button>
      </div>
    `;
  }

  _renderVegRoom() {
    return `
      <h1>🌱 Veg Room</h1>

      ${this._vegRoom.status === 'Not Configured' ? `
        <div class="card">
          <p>Veg room not configured.</p>
          <p>Add it via Home Assistant Settings → Devices & Services → Add Integration → Grow Room Manager → Veg Room</p>
        </div>
      ` : `
        <div class="grid">
          <div class="card">
            <div class="card-title">📊 Status</div>
            <div class="stat">
              <span class="stat-label">Status</span>
              <span class="stat-value">${this._vegRoom.status}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Active Batches</span>
              <span class="stat-value">${this._vegRoom.batchCount}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Total Plants</span>
              <span class="stat-value">${this._vegRoom.totalPlants}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Recommended EC</span>
              <span class="stat-value">${this._vegRoom.recommendedEc}</span>
            </div>
          </div>

          <div class="card">
            <div class="card-title">🌡️ Environment Targets</div>
            <div class="stat">
              <span class="stat-label">Day Temp</span>
              <span class="stat-value">75-82°F</span>
            </div>
            <div class="stat">
              <span class="stat-label">Night Temp</span>
              <span class="stat-value">68-75°F</span>
            </div>
            <div class="stat">
              <span class="stat-label">Humidity</span>
              <span class="stat-value">55-70%</span>
            </div>
            <div class="stat">
              <span class="stat-label">VPD</span>
              <span class="stat-value">0.8-1.2 kPa</span>
            </div>
          </div>
        </div>

        <h2>📦 Batches by Stage</h2>
        <div class="card">
          <table>
            <tr><th>Stage</th><th>Batches</th><th>Plants</th></tr>
            ${Object.entries(this._vegRoom.batchesByStage).map(([stage, data]) => `
              <tr>
                <td><span class="badge badge-${stage.toLowerCase().replace(/[- ]/g, '')}">${stage}</span></td>
                <td>${data.count}</td>
                <td>${data.plants}</td>
              </tr>
            `).join('') || '<tr><td colspan="3">No batches</td></tr>'}
          </table>
        </div>

        <h2>➕ Add New Batch</h2>
        <div class="card">
          <div class="grid">
            <div>
              <label>Batch Name</label>
              <input type="text" class="input" id="batch-name" placeholder="e.g., Clones Dec 2024">
            </div>
            <div>
              <label>Stage</label>
              <select class="input" id="batch-stage">
                <option value="Clone">Clone</option>
                <option value="Pre-Veg">Pre-Veg</option>
                <option value="Early Veg">Early Veg</option>
                <option value="Late Veg">Late Veg</option>
                <option value="Mother">Mother</option>
              </select>
            </div>
            <div>
              <label>Plant Count</label>
              <input type="number" class="input" id="batch-count" value="24">
            </div>
            <div>
              <label>Strain</label>
              <input type="text" class="input" id="batch-strain" placeholder="Optional">
            </div>
            <div>
              <label>Destination Room</label>
              <select class="input" id="batch-dest">
                <option value="f1">F1</option>
                <option value="f2">F2</option>
                <option value="f3">F3</option>
                <option value="none">None</option>
              </select>
            </div>
          </div>
          <button class="btn btn-success" data-action="add-batch-submit" style="margin-top: 15px">🌱 Add Batch</button>
        </div>

        <h2>📋 Active Batches</h2>
        <div class="card">
          <table>
            <tr><th>Name</th><th>Stage</th><th>Plants</th><th>Strain</th><th>Dest</th><th>Actions</th></tr>
            ${this._vegRoom.batches.map(b => `
              <tr>
                <td>${b.name}</td>
                <td><span class="badge badge-${b.stage?.toLowerCase().replace(/[- ]/g, '')}">${b.stage}</span></td>
                <td>${b.plants}</td>
                <td>${b.strain || '-'}</td>
                <td>${b.destination || '-'}</td>
                <td>
                  <button class="btn" style="padding: 5px 10px; font-size: 12px" data-action="update-batch" data-batch="${b.batch_id}">📝</button>
                </td>
              </tr>
            `).join('') || '<tr><td colspan="6">No active batches</td></tr>'}
          </table>
        </div>

        <h2>⚡ Quick Add</h2>
        <div class="quick-btns">
          <button class="btn" data-action="quick-batch" data-stage="Clone" data-count="24">🌱 24 Clones</button>
          <button class="btn" data-action="quick-batch" data-stage="Clone" data-count="12">🌱 12 Clones</button>
          <button class="btn" data-action="quick-batch" data-stage="Mother" data-count="1">👑 Mother</button>
        </div>
      `}
    `;
  }


  _renderJournal() {
    return `
      <h1>📝 Journal</h1>

      <div class="tabs">
        <div class="tab active" data-journal-room="f1">F1</div>
        <div class="tab" data-journal-room="f2">F2</div>
        <div class="tab" data-journal-room="f3">F3</div>
        <div class="tab" data-journal-room="veg">Veg</div>
      </div>

      <div class="card">
        <div class="card-title">➕ Add Entry</div>
        <input type="text" class="input" id="journal-note" placeholder="Enter your note...">
        <div class="quick-btns">
          <button class="btn" data-action="journal-quick" data-note="All plants healthy">✅ All Good</button>
          <button class="btn" data-action="journal-quick" data-note="Fed plants">💧 Fed</button>
          <button class="btn" data-action="journal-quick" data-note="IPM spray completed">🐛 IPM</button>
          <button class="btn" data-action="journal-quick" data-note="Defoliation completed">✂️ Pruned</button>
          <button class="btn" data-action="journal-quick" data-note="EC/pH checked and adjusted">📊 EC Check</button>
          <button class="btn" data-action="journal-quick" data-note="Issue found - needs attention">⚠️ Issue</button>
        </div>
        <button class="btn btn-success" data-action="journal-submit">💾 Save Note</button>
      </div>

      <h2>📖 Recent Entries</h2>
      <div id="journal-entries">
        <p style="color: var(--text-secondary)">Select a room tab to view entries. Entries are stored in /config/grow_logs/</p>
      </div>

      <h2>📤 Export</h2>
      <div class="quick-btns">
        <button class="btn btn-secondary" data-action="export-journal" data-room="f1">Export F1</button>
        <button class="btn btn-secondary" data-action="export-journal" data-room="f2">Export F2</button>
        <button class="btn btn-secondary" data-action="export-journal" data-room="f3">Export F3</button>
        <button class="btn btn-secondary" data-action="export-journal" data-room="veg">Export Veg</button>
      </div>
    `;
  }

  _renderFeeding() {
    return `
      <h1>🧪 Feeding Calculator</h1>

      <div class="grid">
        <div class="card">
          <div class="card-title">🌸 Flower - Current Phases</div>
          ${['f1', 'f2', 'f3'].map(id => {
            const room = this._rooms[id];
            if (!room?.configured) return '';
            return `<div class="stat">
              <span class="stat-label">${id.toUpperCase()}</span>
              <span class="stat-value">Day ${room.day || '-'} - ${room.phase} (EC ${room.ec || '-'})</span>
            </div>`;
          }).join('')}
        </div>

        <div class="card">
          <div class="card-title">🌱 Veg - Recommended</div>
          <div class="stat">
            <span class="stat-label">EC Target</span>
            <span class="stat-value">${this._vegRoom.recommendedEc}</span>
          </div>
        </div>
      </div>

      <h2>🌸 Flower Recipes</h2>
      <div class="grid">
        <div class="card">
          <div class="card-title">Core + Bloom (Stretch/Bulk)</div>
          <p style="color: var(--accent-green)">Target EC: 3.0 | pH: 5.8-6.0</p>
          <table>
            <tr><th>Tank</th><th>Core</th><th>Bloom</th></tr>
            <tr><td>20L</td><td>16g</td><td>16g</td></tr>
            <tr><td>50L</td><td>40g</td><td>40g</td></tr>
            <tr><td>100L</td><td>79g</td><td>79g</td></tr>
            <tr><td>200L</td><td>158g</td><td>158g</td></tr>
          </table>
        </div>

        <div class="card">
          <div class="card-title">Fade (Finish Phase)</div>
          <p style="color: var(--accent-green)">Target EC: 1.5 | pH: 5.8-6.0</p>
          <table>
            <tr><th>Tank</th><th>Fade</th><th>Cleanse</th></tr>
            <tr><td>20L</td><td>16g</td><td>5g</td></tr>
            <tr><td>50L</td><td>40g</td><td>13g</td></tr>
            <tr><td>100L</td><td>79g</td><td>26g</td></tr>
            <tr><td>200L</td><td>158g</td><td>52g</td></tr>
          </table>
        </div>
      </div>

      <h2>🌱 Veg Recipes</h2>
      <div class="card">
        <div class="card-title">Core + Grow + Balance</div>
        <p style="color: var(--accent-green)">pH: 5.8-6.2 | Add pH Down as needed</p>
        <table>
          <tr><th>Stage</th><th>Core/gal</th><th>Grow/gal</th><th>Balance/gal</th><th>EC</th></tr>
          <tr><td><span class="badge badge-clone">Clone</span></td><td>1g</td><td>1g</td><td>0.5g</td><td>0.8</td></tr>
          <tr><td><span class="badge badge-preveg">Pre-Veg</span></td><td>1.5g</td><td>1.5g</td><td>0.5g</td><td>1.2</td></tr>
          <tr><td><span class="badge badge-earlyveg">Early Veg</span></td><td>2g</td><td>2g</td><td>1g</td><td>1.8</td></tr>
          <tr><td><span class="badge badge-lateveg">Late Veg</span></td><td>2.5g</td><td>2.5g</td><td>1g</td><td>2.2</td></tr>
          <tr><td><span class="badge badge-mother">Mother</span></td><td>2g</td><td>2g</td><td>1g</td><td>2.0</td></tr>
        </table>
      </div>

      <h2>📋 Mixing Instructions</h2>
      <div class="card">
        <ol style="line-height: 2">
          <li>Fill tank with RO/filtered water</li>
          <li>Add <strong>Core</strong> first, stir well</li>
          <li>Add <strong>Bloom</strong> (flower) or <strong>Grow</strong> (veg), stir well</li>
          <li>Add <strong>Balance</strong> (veg only) for calcium</li>
          <li>Check EC - adjust if needed</li>
          <li>Add <strong>pH Down</strong> to reach 5.8-6.2</li>
          <li>Let mix 15 minutes before use</li>
        </ol>
        <div class="alert" style="margin-top: 15px">⚠️ Never mix concentrates directly!</div>
      </div>
    `;
  }

  _renderSettings() {
    return `
      <h1>⚙️ Settings</h1>

      <div class="card">
        <div class="card-title">📅 Room Start Dates</div>
        <p style="color: var(--text-secondary); margin-bottom: 15px">
          Set the start date (Day 1 of flower) for each room. This determines the current day and phase.
        </p>
        
        ${['f1', 'f2', 'f3'].map(id => {
          const room = this._rooms[id];
          return `
            <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0; padding: 10px; background: var(--bg-secondary); border-radius: 6px;">
              <strong style="width: 40px">${id.toUpperCase()}</strong>
              <span style="flex: 1; color: var(--text-secondary)">${room?.startDate || 'Not set'}</span>
              <button class="btn" data-action="set-start-today" data-room="${id}">Set Today</button>
            </div>
          `;
        }).join('')}
      </div>

      <div class="card">
        <div class="card-title">📋 Task Generation</div>
        <p style="color: var(--text-secondary); margin-bottom: 15px">
          Generate calendar events and todo items for the 84-day schedule.
          Requires calendar/todo entities configured in HA.
        </p>
        <div class="quick-btns">
          <button class="btn btn-secondary" data-action="generate-tasks" data-room="f1">Generate F1 Tasks</button>
          <button class="btn btn-secondary" data-action="generate-tasks" data-room="f2">Generate F2 Tasks</button>
          <button class="btn btn-secondary" data-action="generate-tasks" data-room="f3">Generate F3 Tasks</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">ℹ️ About</div>
        <p>Grow Room Manager v1.1.0</p>
        <p style="color: var(--text-secondary)">Based on Athena Pro Line methodology</p>
        <p style="color: var(--text-secondary); margin-top: 10px">
          Data stored in: /config/grow_logs/<br>
          Add/remove rooms via: HA Settings → Devices & Services
        </p>
      </div>
    `;
  }


  _renderGuide() {
    return `
      <h1>📖 Athena Pro Line Guide</h1>

      <div class="card">
        <div class="card-title">📊 Phase Overview</div>
        <table>
          <tr><th>Phase</th><th>Days</th><th>EC</th><th>Dryback</th><th>Key Actions</th></tr>
          <tr>
            <td><span class="badge badge-stretch">Stretch</span></td>
            <td>1-21</td><td>3.0</td><td>20-25%</td>
            <td>Defoliation Day 2, IPM sprays</td>
          </tr>
          <tr>
            <td><span class="badge badge-bulk">Bulk</span></td>
            <td>22-55</td><td>3.0</td><td>30-40%</td>
            <td>Maintenance every 3 days</td>
          </tr>
          <tr>
            <td><span class="badge badge-finish">Finish</span></td>
            <td>56-84</td><td>1.5</td><td>40-50%</td>
            <td>Fade nutrients, harvest prep</td>
          </tr>
        </table>
      </div>

      <div class="card">
        <div class="card-title">⚠️ Critical Days</div>
        <table>
          <tr><th>Day</th><th>Action</th></tr>
          <tr><td><strong>Day 2</strong></td><td>Heavy defoliation - strip lower 1/3 of plant</td></tr>
          <tr><td><strong>Day 21</strong></td><td>Final defoliation + LAST IPM spray ever!</td></tr>
          <tr><td><strong>Day 42</strong></td><td>Major maintenance prune for airflow</td></tr>
          <tr><td><strong>Day 56</strong></td><td>Switch to Athena Fade (zero nitrogen)</td></tr>
          <tr><td><strong>Day 77-84</strong></td><td>Harvest window - check trichomes</td></tr>
        </table>
      </div>

      <div class="grid">
        <div class="card">
          <div class="card-title">🌡️ Stretch Environment (Days 1-21)</div>
          <div class="stat"><span class="stat-label">Day Temp</span><span class="stat-value">78-82°F (25-28°C)</span></div>
          <div class="stat"><span class="stat-label">Night Temp</span><span class="stat-value">68-72°F (20-22°C)</span></div>
          <div class="stat"><span class="stat-label">Humidity</span><span class="stat-value">55-65%</span></div>
          <div class="stat"><span class="stat-label">VPD</span><span class="stat-value">1.0-1.2 kPa</span></div>
        </div>

        <div class="card">
          <div class="card-title">🌡️ Bulk Environment (Days 22-55)</div>
          <div class="stat"><span class="stat-label">Day Temp</span><span class="stat-value">78-82°F (25-28°C)</span></div>
          <div class="stat"><span class="stat-label">Night Temp</span><span class="stat-value">65-70°F (18-21°C)</span></div>
          <div class="stat"><span class="stat-label">Humidity</span><span class="stat-value">50-60%</span></div>
          <div class="stat"><span class="stat-label">VPD</span><span class="stat-value">1.2-1.4 kPa</span></div>
        </div>

        <div class="card">
          <div class="card-title">🌡️ Finish Environment (Days 56-84)</div>
          <div class="stat"><span class="stat-label">Day Temp</span><span class="stat-value">75-78°F (24-26°C)</span></div>
          <div class="stat"><span class="stat-label">Night Temp</span><span class="stat-value">62-68°F (17-20°C)</span></div>
          <div class="stat"><span class="stat-label">Humidity</span><span class="stat-value">40-50%</span></div>
          <div class="stat"><span class="stat-label">VPD</span><span class="stat-value">1.4-1.6 kPa</span></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">🐛 IPM Schedule (Stretch Phase Only)</div>
        <p>Apply IPM spray 2x per week during stretch phase:</p>
        <p style="font-size: 18px; margin: 15px 0"><strong>Days 3, 7, 10, 14, 17, 21</strong></p>
        <div class="alert">⚠️ NO SPRAYS AFTER DAY 21! Use biological controls only after this point.</div>
      </div>

      <div class="card">
        <div class="card-title">🌱 Veg Stages</div>
        <table>
          <tr><th>Stage</th><th>Duration</th><th>EC</th><th>Notes</th></tr>
          <tr><td><span class="badge badge-clone">Clone</span></td><td>~14 days</td><td>0.8</td><td>High humidity dome, rooting</td></tr>
          <tr><td><span class="badge badge-preveg">Pre-Veg</span></td><td>~7 days</td><td>1.2</td><td>Post-transplant establishment</td></tr>
          <tr><td><span class="badge badge-earlyveg">Early Veg</span></td><td>~14 days</td><td>1.8</td><td>Rapid growth, training begins</td></tr>
          <tr><td><span class="badge badge-lateveg">Late Veg</span></td><td>~14 days</td><td>2.2</td><td>Final growth, ready for flower</td></tr>
          <tr><td><span class="badge badge-mother">Mother</span></td><td>Ongoing</td><td>2.0</td><td>Maintained for cuttings</td></tr>
        </table>
      </div>
    `;
  }

  _attachEventListeners() {
    // Tab switching for flower rooms
    this.shadowRoot.querySelectorAll('.tab[data-room]').forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.shadowRoot.querySelectorAll('.tab[data-room]').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        const content = this.shadowRoot.getElementById('flower-room-content');
        if (content) {
          content.innerHTML = this._renderFlowerRoomDetail(e.target.dataset.room);
          this._attachEventListeners();
        }
      });
    });

    // Quick note buttons
    this.shadowRoot.querySelectorAll('[data-action="quick-note"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const room = e.target.dataset.room;
        const note = e.target.dataset.note;
        this._addJournalEntry(room, note);
      });
    });

    // Custom note
    this.shadowRoot.querySelectorAll('[data-action="custom-note"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const room = e.target.dataset.room;
        const input = this.shadowRoot.getElementById(`custom-note-${room}`);
        if (input?.value) {
          this._addJournalEntry(room, input.value);
          input.value = '';
        }
      });
    });

    // Set start date
    this.shadowRoot.querySelectorAll('[data-action="set-start-today"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const room = e.target.dataset.room;
        this._setStartDate(room);
      });
    });

    // Generate tasks
    this.shadowRoot.querySelectorAll('[data-action="generate-tasks"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const room = e.target.dataset.room;
        this._generateTasks(room);
      });
    });

    // Export journal
    this.shadowRoot.querySelectorAll('[data-action="export-journal"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const room = e.target.dataset.room;
        this._exportJournal(room);
      });
    });

    // Quick batch add
    this.shadowRoot.querySelectorAll('[data-action="quick-batch"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const stage = e.target.dataset.stage;
        const count = parseInt(e.target.dataset.count);
        this._addQuickBatch(stage, count);
      });
    });

    // Add batch form submit
    this.shadowRoot.querySelectorAll('[data-action="add-batch-submit"]').forEach(btn => {
      btn.addEventListener('click', () => this._addBatchFromForm());
    });

    // Journal quick notes
    this.shadowRoot.querySelectorAll('[data-action="journal-quick"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const input = this.shadowRoot.getElementById('journal-note');
        if (input) input.value = e.target.dataset.note;
      });
    });

    // Journal submit
    this.shadowRoot.querySelectorAll('[data-action="journal-submit"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = this.shadowRoot.getElementById('journal-note');
        const activeTab = this.shadowRoot.querySelector('.tab[data-journal-room].active');
        const room = activeTab?.dataset.journalRoom || 'f1';
        if (input?.value) {
          this._addJournalEntry(room, input.value);
          input.value = '';
        }
      });
    });

    // Journal room tabs
    this.shadowRoot.querySelectorAll('.tab[data-journal-room]').forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.shadowRoot.querySelectorAll('.tab[data-journal-room]').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
      });
    });
  }


  // Service call methods
  async _addJournalEntry(roomId, note) {
    try {
      await this._hass.callService('grow_room_manager', 'add_journal_entry', {
        room_id: roomId,
        note: note
      });
      this._showNotification(`✅ Note added to ${roomId.toUpperCase()}`);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  async _setStartDate(roomId) {
    const today = new Date().toISOString().split('T')[0];
    try {
      await this._hass.callService('grow_room_manager', 'set_start_date', {
        room_id: roomId,
        start_date: today
      });
      this._showNotification(`✅ ${roomId.toUpperCase()} start date set to ${today}`);
      setTimeout(() => this._loadData(), 1000);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  async _generateTasks(roomId) {
    const room = this._rooms[roomId];
    if (!room?.startDate) {
      this._showNotification('❌ Set start date first', true);
      return;
    }
    try {
      await this._hass.callService('grow_room_manager', 'generate_tasks', {
        room_id: roomId,
        start_date: room.startDate
      });
      this._showNotification(`✅ Tasks generated for ${roomId.toUpperCase()}`);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  async _exportJournal(roomId) {
    try {
      await this._hass.callService('grow_room_manager', 'export_journal', {
        room_id: roomId,
        format: 'csv'
      });
      this._showNotification(`✅ Journal exported for ${roomId.toUpperCase()}`);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  async _addQuickBatch(stage, count) {
    const today = new Date();
    const name = `${stage} ${today.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    const dateStr = today.toISOString().split('T')[0];
    
    try {
      await this._hass.callService('grow_room_manager', 'add_veg_batch', {
        room_id: 'veg',
        batch_name: name,
        start_date: dateStr,
        stage: stage,
        plant_count: count,
        destination_room: 'f1'
      });
      this._showNotification(`✅ Added ${count} ${stage}`);
      setTimeout(() => this._loadData(), 1000);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  async _addBatchFromForm() {
    const name = this.shadowRoot.getElementById('batch-name')?.value;
    const stage = this.shadowRoot.getElementById('batch-stage')?.value;
    const count = parseInt(this.shadowRoot.getElementById('batch-count')?.value) || 24;
    const strain = this.shadowRoot.getElementById('batch-strain')?.value || '';
    const dest = this.shadowRoot.getElementById('batch-dest')?.value || 'f1';
    
    if (!name) {
      this._showNotification('❌ Enter a batch name', true);
      return;
    }

    const today = new Date().toISOString().split('T')[0];
    
    try {
      await this._hass.callService('grow_room_manager', 'add_veg_batch', {
        room_id: 'veg',
        batch_name: name,
        start_date: today,
        stage: stage,
        plant_count: count,
        strain: strain,
        destination_room: dest
      });
      this._showNotification(`✅ Added batch: ${name}`);
      
      // Clear form
      this.shadowRoot.getElementById('batch-name').value = '';
      this.shadowRoot.getElementById('batch-strain').value = '';
      
      setTimeout(() => this._loadData(), 1000);
    } catch (err) {
      this._showNotification(`❌ Error: ${err.message}`, true);
    }
  }

  _showNotification(message, isError = false) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      padding: 15px 25px;
      background: ${isError ? '#e74c3c' : '#27ae60'};
      color: white;
      border-radius: 8px;
      font-weight: 500;
      z-index: 9999;
      animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    // Add animation keyframes
    if (!this.shadowRoot.querySelector('#notification-styles')) {
      const style = document.createElement('style');
      style.id = 'notification-styles';
      style.textContent = `
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      this.shadowRoot.appendChild(style);
    }
    
    this.shadowRoot.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => notification.remove(), 3000);
  }
}

customElements.define('grow-room-panel', GrowRoomPanel);
