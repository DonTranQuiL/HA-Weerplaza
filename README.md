

<div align="center">

# 🌌 WEERPLAZA Integration for Home Assistant.
**This integration is more advanced than the original within Home Assistant, this one includes as well lightning/thunder detection.**

</div>
<p align="center">
  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/releases">
    <img src="https://img.shields.io/github/v/release/DonTranQuiL/HA-Weerplaza?style=for-the-badge&color=007ec6" alt="Latest Release">
  </a>
  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/DonTranQuiL/HA-Weerplaza?style=for-the-badge&color=007ec6" alt="License">
  </a>
  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/actions/workflows/hass-ci.yml">
    <img src="https://github.com/DonTranQuiL/HA-Weerplaza/actions/workflows/hass-ci.yml/badge.svg" alt="Home Assistant CI" style="height:28px;">
  </a>

  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/HA-Weerplaza/codechecker.yml?style=for-the-badge&label=CODE%20CHECKS&color=5dbb0f" alt="Code Checks">
  </a>
  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/HA-Weerplaza/pytest.yml?style=for-the-badge&label=TESTS&color=5dbb0f" alt="Tests">
  </a>
  <a href="https://github.com/DonTranQuiL/HA-Weerplaza/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/HA-Weerplaza/hacs.yaml?style=for-the-badge&label=HACS%20VALIDATION&color=5dbb0f" alt="HACS Validation">
  </a>

  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-5dbb0f?style=for-the-badge" alt="pre-commit">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-000000?style=for-the-badge" alt="Ruff">
  </a>
  <a href="https://codecov.io/gh/DonTranQuiL/HA-Weerplaza">
    <img src="https://codecov.io/gh/DonTranQuiL/HA-Weerplaza/branch/main/graph/badge.svg" alt="Coverage" style="height:28px;">
  </a>

  <a href="https://hacs.xyz/">
    <img src="https://img.shields.io/badge/HACS-CUSTOM-ff6e27?style=for-the-badge" alt="HACS">
  </a>
  <a href="https://www.home-assistant.io/">
    <img src="https://img.shields.io/badge/Home%20Assistant-2024.5%2B-007ec6?style=for-the-badge" alt="Home Assistant">
  </a>

  <a href="https://github.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/maintainer-%40DonTranQuiL-007ec6?style=for-the-badge" alt="Maintainer">
  </a>
  <a href="https://ko-fi.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-ffdd00?style=for-the-badge" alt="Donate">
  </a>
  <a href="https://community.home-assistant.io/">
    <img src="https://img.shields.io/badge/community-forum-007ec6?style=for-the-badge" alt="Community">
  </a>
</p>

This custom component for Home Assistant allows you to monitor weather data for any location from the Dutch weather site [Weerplaza.nl](https://www.weerplaza.nl/). It works by scraping the data directly from the location's page, providing detailed weather information without requiring an official API.

> **Disclaimer:** This integration relies on web scraping. If Weerplaza.nl changes the HTML structure of its website, this integration will likely break until it is updated. Please be a good citizen and use a reasonable update interval to avoid overloading their servers.

This integration was created with significant collaboration, testing, and debugging from **TranQuiL (@Malosaaa)**.

***
## 🚀 Key Features

* ✅ **L1-Style Persistence**: Includes a built-in cache system. Your weather data is saved to disk and loads **instantly** when Home Assistant reboots—no more "Unknown" states on startup.
* ✅ **Lightning Detection**: Real-time tracking of the nearest lightning strike, including a dedicated `flash_range` attribute (numeric) for easy automations.
* ✅ **Rain & Warning Alerts**: Separate attributes for local rain status (Splash) and official KNMI/Meteo warnings (Code Green/Yellow/Orange/Red).
* ✅ **Advanced Astro Data**: Includes Sunrise, Sunset, and Moon Phases—complete with **official Moon Phase icons** pulled directly from Weerplaza.
* ✅ **Master Sensor Approach**: A single master sensor provides the temperature, while 50+ data points (Hourly/Daily/Astro) are available as organized attributes.
* ✅ **Service Calls**: Includes services to manually trigger a refresh or clear the local cache via Developer Tools.

## 🛠 Installation

### Method 1: HACS (Recommended)
1. Open **HACS** -> **Integrations**.
2. Click the 3-dots menu (top right) -> **Custom Repositories**.
3. Paste URL: `https://github.com/Malosaaa/ha-weerplaza` | Category: **Integration**.
4. Click **Add**, then find "Weerplaza Weather" and click **Download**.
5. **Restart Home Assistant.**

### Method 2: Manual
1. Download the `weerplaza` folder from this repo.
2. Copy it into your Home Assistant `custom_components/` directory.
3. **Restart Home Assistant.**

## ⚙️ Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **+ Add Integration** and search for **Weerplaza Weather**.
3. **Friendly Name**: Choose a name (e.g., `Home`).
4. **Location Path**: Go to Weerplaza.nl, find your city, and copy the URL path after `.nl/`.
   * *Example:* For `https://www.weerplaza.nl/nederland/utrecht/19344/`, use `nederland/utrecht/19344/`.
5. **Scan Interval**: Set how often to check for updates (1800 seconds recommended).

## 📊 Sensors & Attributes

### Master Sensor
`sensor.weerplaza_<name>_current_weather`

| Attribute | Content |
| :--- | :--- |
| `flash_detection` | Text description of nearest lightning (e.g., "Bliksem op 10km"). |
| `flash_range` | Numeric distance of lightning (Ideal for automations). |
| `rain` | Local rain status (e.g., "Droog" or "Lichte regen"). |
| `alerts` | Official Meteo warnings (e.g., "Er zijn nu geen waarschuwingen"). |
| `daily_forecast_summary` | 7-14 day forecast including `temp_high`, `temp_low`, and `date_short`. |
| `astro` | Sunrise and Sunset times. |
| `moon_phases` | Upcoming phases with specific Image URLs. |

## 🛠 Services

| Service | Description |
| :--- | :--- |
| `weerplaza.manual_refresh` | Forces an immediate scrape of the website. |
| `weerplaza.clear_cache` | Deletes the local `.storage` cache file. |


## 🎨 Recommended Dashboard (Mushroom)

To get the look seen in the screenshots, you will need **[Mushroom Cards](https://github.com/piitaya/lovelace-mushroom)** and **[Card Mod](https://github.com/thomasloven/lovelace-card-mod)** (both available in HACS). 

*Note: Replace `yourplace` in the entity IDs below with your actual instance name.*

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    entity: sensor.weerplaza_yourplace_current_weather
    primary: "{{ state_attr(entity, 'current_weather').description_icon_title }}"
    secondary: "{{ state_attr(entity, 'current_weather').temperature }}°C · {{ state_attr(entity, 'current_weather').location_name_observed }}"
    picture: "{{ state_attr(entity, 'current_weather').icon }}"
    layout: vertical
    card_mod:
      style: |
        mushroom-template-card {
          background: linear-gradient(to right, #fffde7, #e0f2f1);
          border-radius: 1rem;
        }

  - type: grid
    columns: 2
    square: false
    cards:
      - type: custom:mushroom-template-card
        primary: "{{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[0].date_short }}"
        secondary: "H: {{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[0].temp_high }}° · L: {{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[0].temp_low }}°"
        picture: "{{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[0].icon }}"
        layout: vertical
      - type: custom:mushroom-template-card
        primary: "{{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[1].date_short }}"
        secondary: "H: {{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[1].temp_high }}° · L: {{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[1].temp_low }}°"
        picture: "{{ state_attr('sensor.weerplaza_yourplace_current_weather', 'daily_forecast_summary')[1].icon }}"
        layout: vertical

  - type: custom:mushroom-template-card
    entity: sensor.weerplaza_yourplace_current_weather
    primary: "⚡ Bliksem & Regen Status"
    secondary: "{{ state_attr(entity, 'flash_detection') }} | Regen: {{ state_attr(entity, 'rain') }}"
    icon: mdi:flash-alert
    icon_color: "{% if state_attr(entity, 'flash_range') | float < 100 %} red {% else %} amber {% endif %}"
    card_mod:
      style: |
        mushroom-template-card {
          background-color: #fff3cd;
          border-left: 5px solid #ff9800;
        }
```
<img width="363" height="679" alt="{F1C45BE3-054E-43FA-8425-D72B2C05F887}" src="https://github.com/user-attachments/assets/173ea33e-023c-4344-8ba5-5a15f0fe6788" />


[hacs]: https://hacs.xyz
[hacs_badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[maintenance_badge]: https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge
