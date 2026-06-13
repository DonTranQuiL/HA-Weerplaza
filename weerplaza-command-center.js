class WeerplazaCommandCenter extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define the Weerplaza entity');
    }
    this.config = config;
  }

  // Safely extract numbers from messy strings to prevent encoding glitches
  _cleanTemp(val) {
    if (val === undefined || val === null) return '--';
    return val.toString().replace(/[^0-9.-]/g, '');
  }

  // Detect condition keywords to drive live background animations
  _getWeatherEffect(title, iconUrl) {
    const text = ((title || '') + (iconUrl || '')).toLowerCase();
    if (text.includes('onweer') || text.includes('thunder') || text.includes('bliksem')) return 'thunderstorm';
    if (text.includes('regen') || text.includes('bui') || text.includes('rain') || text.includes('drizzle')) return 'rain';
    if (text.includes('sneeuw') || text.includes('snow') || text.includes('hagel')) return 'snow';
    if (text.includes('zonnig') || text.includes('helder') || text.includes('sun') || text.includes('clear')) return 'sunny';
    return 'cloudy';
  }

  set hass(hass) {
    const entityId = this.config.entity;
    const stateObj = hass.states[entityId];

    if (!stateObj) {
      this.shadowRoot.innerHTML = `
        <ha-card style="padding: 16px; color: var(--error-color); background: var(--card-background-color);">
          Entity not found: <strong>${entityId}</strong>
        </ha-card>
      `;
      return;
    }

    const attrs = stateObj.attributes || {};
    const current = attrs.current_weather || {};
    const hourly = attrs.hourly_forecast || [];
    const daily = attrs.daily_forecast_summary || [];
    const moon = attrs.moon_phases || [];
    const alerts = attrs.alerts || 'Geen waarschuwingen';
    const flashDetection = attrs.flash_detection || 'Geen activiteit';
    const flashRange = parseFloat(attrs.flash_range);
    const rain = attrs.rain || '0 mm';

    const hasAlert = alerts.toLowerCase() !== 'geen' && !alerts.toLowerCase().includes('geen waarschuwing');
    const alertClass = hasAlert ? 'status-alert pulse' : 'status-safe';
    const lightningClass = (!isNaN(flashRange) && flashRange < 100) ? 'status-warning pulse' : 'status-normal';
    
    // Get the dynamic weather effect class name
    const fxClass = this._getWeatherEffect(current.description_icon_title, current.icon);

    // Safely encode static text terms to bypass encoding errors
    const safeAlertTitle = "Offici&euml;le Weerwaarschuwing";

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --card-padding: 16px;
          --border-radius: 16px;
          --glass-bg: var(--ha-card-background, var(--card-background-color, rgba(255, 255, 255, 0.05)));
        }
        
        ha-card {
          background: var(--glass-bg);
          border-radius: var(--border-radius);
          padding: var(--card-padding);
          font-family: var(--paper-font-body1_-_font-family), BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          color: var(--primary-text-color);
          box-shadow: var(--ha-card-box-shadow, none);
          border: 1px solid var(--divider-color, rgba(255, 255, 255, 0.1));
          position: relative;
          overflow: hidden;
          z-index: 1;
        }

        /* LIVE WEATHER ANIMATION EFFECTS LAYER */
        .weather-fx-layer {
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          pointer-events: none;
          z-index: -1;
          opacity: 0.18;
          overflow: hidden;
        }

        /* Rain Effect */
        .weather-fx-layer.rain {
          background: linear-gradient(transparent, rgba(0,0,0,0.1));
        }
        .weather-fx-layer.rain::before {
          content: '';
          position: absolute;
          width: 200%; height: 200%;
          top: -50%; left: -50%;
          background: repeating-linear-gradient(0deg, transparent, transparent 20px, var(--primary-text-color) 20px, var(--primary-text-color) 40px);
          mask-image: radial-gradient(ellipse at center, white, transparent);
          transform: rotate(-15deg);
          animation: falling-rain 0.8s linear infinite;
        }

        /* Thunderstorm Effect (Rain + Lightning flashes) */
        .weather-fx-layer.thunderstorm {
          animation: lightning-flash 6s ease-in-out infinite;
        }
        .weather-fx-layer.thunderstorm::before {
          content: '';
          position: absolute;
          width: 200%; height: 200%;
          top: -50%; left: -50%;
          background: repeating-linear-gradient(0deg, transparent, transparent 15px, #90caf9 15px, #90caf9 35px);
          transform: rotate(-20deg);
          animation: falling-rain 0.5s linear infinite;
        }

        /* Snow Effect */
        .weather-fx-layer.snow::before {
          content: '•  •   •  •  •  •   •  •';
          font-size: 24px;
          color: var(--primary-text-color);
          position: absolute;
          top: -40px; left: 0; right: 0;
          word-spacing: 20px;
          text-shadow: 0 50px, 50px 100px, 20px 200px, 80px 250px, 10px 300px;
          animation: falling-snow 8s linear infinite;
        }

        /* Sunny Effect */
        .weather-fx-layer.sunny {
          background: radial-gradient(circle at 90% 10%, rgba(255, 193, 7, 0.4) 0%, transparent 60%);
          animation: solar-pulse 4s ease-in-out infinite alternate;
        }

        /* Cloudy Drift */
        .weather-fx-layer.cloudy::before {
          content: '';
          position: absolute;
          top: 0; left: 0; width: 200%; height: 100%;
          background: radial-gradient(circle at 30% 50%, rgba(var(--rgb-primary-text-color), 0.05) 0%, transparent 40%);
          animation: cloud-drift 20s linear infinite;
        }

        /* ANIMATION KEYFRAMES */
        @keyframes falling-rain {
          0% { transform: translate(0, 0) rotate(-15deg); }
          100% { transform: translate(-30px, 60px) rotate(-15deg); }
        }
        @keyframes falling-snow {
          0% { transform: translateY(0) rotate(0deg); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(400px) rotate(10deg); opacity: 0; }
        }
        @keyframes solar-pulse {
          0% { opacity: 0.15; transform: scale(1); }
          100% { opacity: 0.3; transform: scale(1.1); }
        }
        @keyframes cloud-drift {
          0% { transform: translateX(-50%); }
          100% { transform: translateX(50%); }
        }
        @keyframes lightning-flash {
          0%, 94%, 98%, 100% { background: transparent; }
          95%, 97% { background: rgba(255, 255, 255, 0.25); box-shadow: inset 0 0 40px rgba(255,255,255,0.4); }
        }

        /* Layout Architecture */
        .header-container {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 20px;
          border-bottom: 1px solid var(--divider-color, rgba(255, 255, 255, 0.08));
          padding-bottom: 16px;
        }
        .header-title-area {
          display: flex;
          flex-direction: column;
        }
        .header-title {
          font-size: 1.4rem;
          font-weight: 700;
          letter-spacing: -0.5px;
          color: var(--primary-text-color);
        }
        .header-subtitle {
          font-size: 0.85rem;
          color: var(--secondary-text-color);
          margin-top: 4px;
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .header-subtitle ha-icon {
          --mdc-icon-size: 16px;
          color: var(--error-color);
        }
        .hero-temp-block {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .hero-temp {
          font-size: 2.2rem;
          font-weight: 800;
          color: var(--primary-text-color);
        }
        .hero-icon {
          width: 54px;
          height: 54px;
          object-fit: contain;
          animation: hero-breathe 4s ease-in-out infinite;
        }

        @keyframes hero-breathe {
          0%, 100% { transform: scale(1); filter: drop-shadow(0 0 0px transparent); }
          50% { transform: scale(1.05); filter: drop-shadow(0 4px 10px rgba(var(--rgb-primary-text-color), 0.15)); }
        }

        .section-label {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: var(--secondary-text-color);
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .section-label ha-icon {
          --mdc-icon-size: 16px;
        }

        /* Hourly Strip */
        .hourly-wrapper {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          margin-bottom: 20px;
        }
        .hourly-card {
          background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.03);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.05));
          border-radius: 10px;
          padding: 10px 6px;
          text-align: center;
          backdrop-filter: blur(4px);
          transition: transform 0.2s ease, background-color 0.2s ease;
        }
        .hourly-card:hover {
          transform: translateY(-2px);
          background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.07);
        }
        .hourly-time {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--secondary-text-color);
        }
        .hourly-icon {
          width: 32px;
          height: 32px;
          margin: 6px auto;
        }
        .hourly-temp {
          font-size: 0.9rem;
          font-weight: 700;
        }

        /* Daily Grid */
        .daily-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          margin-bottom: 20px;
        }
        .daily-row {
          display: flex;
          align-items: center;
          background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.02);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.04));
          border-radius: 12px;
          padding: 8px 12px;
          justify-content: space-between;
          backdrop-filter: blur(4px);
        }
        .daily-date {
          font-size: 0.85rem;
          font-weight: 600;
        }
        .daily-right {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .daily-icon {
          width: 28px;
          height: 28px;
        }
        .daily-range {
          font-size: 0.8rem;
          font-weight: 700;
        }
        .temp-high { color: var(--error-color, #ff5252); margin-right: 2px;}
        .temp-low { color: var(--info-color, #2196f3); }

        /* Alerts & Logs Area */
        .status-box {
          border-radius: 12px;
          padding: 12px;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 12px;
          border: 1px solid transparent;
          backdrop-filter: blur(6px);
        }
        .status-safe {
          background: rgba(76, 175, 80, 0.06);
          border-color: rgba(76, 175, 80, 0.15);
        }
        .status-alert {
          background: rgba(244, 67, 54, 0.1);
          border-color: rgba(244, 67, 54, 0.3);
        }
        .status-normal {
          background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.03);
          border-color: var(--divider-color);
        }
        .status-warning {
          background: rgba(255, 152, 0, 0.1);
          border-color: rgba(255, 152, 0, 0.3);
        }
        .status-icon {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .status-icon ha-icon {
          --mdc-icon-size: 22px;
        }
        .status-safe ha-icon { color: #4caf50; }
        .status-alert ha-icon { color: #f44336; }
        .status-normal ha-icon { color: var(--secondary-text-color); }
        .status-warning ha-icon { color: #ff9800; }
        
        .status-text {
          display: flex;
          flex-direction: column;
          flex: 1;
        }
        .status-title {
          font-size: 0.85rem;
          font-weight: 700;
        }
        .status-desc {
          font-size: 0.8rem;
          color: var(--secondary-text-color);
          margin-top: 2px;
        }

        .pulse {
          animation: panel-glow 2s infinite alternate;
        }
        @keyframes panel-glow {
          0% { box-shadow: 0 0 2px rgba(var(--rgb-error-color), 0.1); }
          100% { box-shadow: 0 0 10px rgba(var(--rgb-error-color), 0.3); }
        }

        /* Astronomy System Footer */
        .moon-row {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          margin-top: 8px;
        }
        .moon-card {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.01);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.03));
          padding: 8px 10px;
          border-radius: 10px;
        }
        .moon-img {
          width: 24px;
          height: 24px;
        }
      </style>

      <ha-card>
        <!-- Particle & Atmosphere VFX Layer -->
        <div class="weather-fx-layer ${fxClass}"></div>

        <!-- Hero Header -->
        <div class="header-container">
          <div class="header-title-area">
            <span class="header-title">${current.description_icon_title || 'Weerplaza'}</span>
            <span class="header-subtitle">
              <ha-icon icon="mdi:map-marker"></ha-icon>
              ${current.location_name_observed || 'Eygelshoven'}
            </span>
          </div>
          <div class="hero-temp-block">
            <span class="hero-temp">${this._cleanTemp(current.temperature)}&deg;C</span>
            ${current.icon ? `<img class="hero-icon" src="${current.icon}" alt="Weather Status" />` : ''}
          </div>
        </div>

        <!-- Hourly Strip Section -->
        <div class="section-label">
          <ha-icon icon="mdi:clock-outline"></ha-icon> Komende Uren
        </div>
        <div class="hourly-wrapper">
          ${hourly.slice(0, 4).map(h => `
            <div class="hourly-card">
              <div class="hourly-time">${h.time || '--:--'}</div>
              <img class="hourly-icon" src="${h.icon}" alt="hour preview"/>
              <div class="hourly-temp">${this._cleanTemp(h.temperature)}&deg;C</div>
            </div>
          `).join('')}
        </div>

        <!-- Multi-Day Forecast Grid -->
        <div class="section-label">
          <ha-icon icon="mdi:calendar-month"></ha-icon> Meerdaagse Verwachting
        </div>
        <div class="daily-grid">
          ${daily.slice(0, 4).map(d => `
            <div class="daily-row">
              <div class="daily-date">${d.date_short || '--'}</div>
              <div class="daily-right">
                <img class="daily-icon" src="${d.icon}" alt="day preview"/>
                <div class="daily-range">
                  <span class="temp-high">${this._cleanTemp(d.temp_high)}&deg;</span> 
                  <span class="temp-low">${this._cleanTemp(d.temp_low)}&deg;</span>
                </div>
              </div>
            </div>
          `).join('')}
        </div>

        <!-- Warning Alert Panel -->
        <div class="status-box ${alertClass}">
          <div class="status-icon">
            <ha-icon icon="mdi:alert-octagon"></ha-icon>
          </div>
          <div class="status-text">
            <div class="status-title">${safeAlertTitle}</div>
            <div class="status-desc">${alerts}</div>
          </div>
        </div>

        <!-- Lightning Feed Status Tracker -->
        <div class="status-box ${lightningClass}">
          <div class="status-icon">
            <ha-icon icon="mdi:flash-alert"></ha-icon>
          </div>
          <div class="status-text">
            <div class="status-title">Bliksem &amp; Neerslag Monitor</div>
            <div class="status-desc">${flashDetection} | Regen: ${rain}</div>
          </div>
        </div>

        <!-- Astro Space Tracking Details -->
        <div class="section-label" style="margin-top: 16px;">
          <ha-icon icon="mdi:moon-waning-gibbous"></ha-icon> Astronomische Status
        </div>
        <div class="moon-row">
          ${moon.slice(0, 2).map(m => `
            <div class="moon-card">
              <img class="moon-img" src="${m.icon}" alt="moon state"/>
              <div class="status-text">
                <div class="status-title" style="font-size: 0.75rem;">${m.phase}</div>
                <div class="status-desc" style="font-size: 0.7rem;">${m.datetime}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 5;
  }
}

customElements.define('weerplaza-command-center', WeerplazaCommandCenter);
