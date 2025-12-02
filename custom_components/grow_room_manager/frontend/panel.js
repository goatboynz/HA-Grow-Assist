/**
 * Grow Room Manager Panel
 * Custom panel for Home Assistant sidebar
 */

class GrowRoomPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialize();
      this._initialized = true;
    }
    this._updateContent();
  }

  _initialize() {
    const style = document.createElement('style');
    style.textContent = `
      :host {
        display: block;
        height: 100%;
        background: var(--primary-background-color);
        color: var(--primary-text-color);
        font-family: var(--paper-font-body1_-_font-family);
      }
      .container {
        padding: 16px;
        max-width: 1200px;
        margin: 0 auto;
      }
      h1 {
        color: var(--primary-text-color);
        margin: 0 0 16px 0;
        font-size: 24px;
      }
      .info-box {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
      }
      .rooms-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
      }
      .room-card {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
      }
      .room-card h3 {
        margin: 0 0 8px 0;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .room-card .status {
        font-size: 18px;
        font-weight: bold;
        color: var(--primary-color);
      }
      .room-card .details {
        color: var(--secondary-text-color);
        font-size: 14px;
      }
      .progress-bar {
        height: 8px;
        background: var(--divider-color);
        border-radius: 4px;
        margin: 8px 0;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        background: var(--primary-color);
        border-radius: 4px;
        transition: width 0.3s;
      }
      .btn {
        background: var(--primary-color);
        color: var(--text-primary-color);
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin: 4px;
      }
      .btn:hover {
        opacity: 0.9;
      }
      .section-title {
        font-size: 18px;
        font-weight: 500;
        margin: 24px 0 12px 0;
        color: var(--primary-text-color);
      }
      a {
        color: var(--primary-color);
      }
    `;
    this.shadowRoot.appendChild(style);

    const container = document.createElement('div');
    container.className = 'container';
    container.innerHTML = `
      <h1>🌿 Grow Room Manager</h1>
      <div class="info-box">
        <p>Welcome to Grow Room Manager! This panel shows an overview of your grow rooms.</p>
        <p>For the full dashboard experience, <a href="/lovelace-grow-rooms" target="_top">click here</a> 
        or add the dashboard manually via Settings → Dashboards.</p>
      </div>
      <div class="section-title">🌸 Flower Rooms</div>
      <div class="rooms-grid" id="flower-rooms"></div>
      <div class="section-title">🌱 Veg Room</div>
      <div class="rooms-grid" id="veg-rooms"></div>
    `;
    this.shadowRoot.appendChild(container);
  }

  _updateContent() {
    if (!this._hass) return;

    const flowerRoomsContainer = this.shadowRoot.getElementById('flower-rooms');
    const vegRoomsContainer = this.shadowRoot.getElementById('veg-rooms');
    
    if (!flowerRoomsContainer || !vegRoomsContainer) return;

    // Flower rooms
    const flowerRooms = [
      { id: 'f1', name: 'Flower Room 1', sensor: 'sensor.flower_room_1_grow_status', progress: 'sensor.flower_room_1_grow_progress' },
      { id: 'f2', name: 'Flower Room 2', sensor: 'sensor.flower_room_2_grow_status', progress: 'sensor.flower_room_2_grow_progress' },
      { id: 'f3', name: 'Flower Room 3', sensor: 'sensor.flower_room_3_grow_status', progress: 'sensor.flower_room_3_grow_progress' },
    ];

    flowerRoomsContainer.innerHTML = flowerRooms.map(room => {
      const state = this._hass.states[room.sensor];
      const progressState = this._hass.states[room.progress];
      
      if (!state) {
        return `
          <div class="room-card">
            <h3>🌸 ${room.name}</h3>
            <div class="status">Not Configured</div>
            <div class="details">Add this room via Settings → Devices & Services</div>
          </div>
        `;
      }

      const status = state.state;
      const phase = state.attributes.phase || 'Unknown';
      const day = state.attributes.current_day || '-';
      const week = state.attributes.current_week || '-';
      const ec = state.attributes.recommended_ec || '-';
      const daysLeft = state.attributes.days_remaining || '-';
      const progress = progressState ? progressState.state : 0;

      return `
        <div class="room-card">
          <h3>🌸 ${room.name}</h3>
          <div class="status">${status}</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${progress}%"></div>
          </div>
          <div class="details">
            Week ${week} | ${phase} Phase<br>
            EC: ${ec} | Days Left: ${daysLeft}
          </div>
        </div>
      `;
    }).join('');

    // Veg room
    const vegState = this._hass.states['sensor.veg_room_status'];
    const vegBatches = this._hass.states['sensor.veg_room_active_batches'];

    if (!vegState) {
      vegRoomsContainer.innerHTML = `
        <div class="room-card">
          <h3>🌱 Veg Room</h3>
          <div class="status">Not Configured</div>
          <div class="details">Add a veg room via Settings → Devices & Services</div>
        </div>
      `;
    } else {
      const status = vegState.state;
      const totalPlants = vegState.attributes.total_plants || 0;
      const batchCount = vegBatches ? vegBatches.state : 0;
      const batches = vegState.attributes.batches_by_stage || {};

      let batchDetails = '';
      for (const [stage, data] of Object.entries(batches)) {
        batchDetails += `${stage}: ${data.count} batches (${data.plants} plants)<br>`;
      }

      vegRoomsContainer.innerHTML = `
        <div class="room-card">
          <h3>🌱 Veg Room</h3>
          <div class="status">${status}</div>
          <div class="details">
            ${batchCount} active batches | ${totalPlants} total plants<br>
            ${batchDetails || 'No batches'}
          </div>
        </div>
      `;
    }
  }
}

customElements.define('grow-room-panel', GrowRoomPanel);
