from custom_components.weerplaza.parser import WeerplazaParser

FULL_SAMPLE_HTML = """
<html>
<body>
    <a class="btn-splash-test"><span class="text">Lichte regen</span></a>
    <a class="btn-flash-alert"><span class="text">Onweer gedetecteerd binnen 15km</span></a>
    <div class="meteo-warning-block"><span class="text">Met waarschuwingen</span></div>
    
    <div class="forecast-astro-container">
        <div><b>Zon op</b> 05:45</div>
        <div><b>Zon onder</b> 21:30</div>
        <div class="col">Volle maan<img src="/assets/moon.png"/> 23 Mei</div>
    </div>

    <div id="hourly">
        <div class="hour">
            <div class="head-time"><div>14:00</div></div>
            <div class="wx" style="background-image: url('wx-sun.png');"></div>
            <div class="temp-val">19&deg;C</div>
        </div>
    </div>

    <div id="fullday">
        <table>
            <tr>
                <td data-day="day1">
                    <div class="show-large">Maandag <div class="date">20 Mei</div></div>
                    <div class="wx" title="Zonnig" style="background-image: url('sun.png');"></div>
                    <div class="red temp">22&deg;C</div>
                    <div class="blue temp">11&deg;</div>
                </td>
            </tr>
        </table>
    </div>

    <div class="location-widget-main">
        <h2>Het weer nu in Utrecht</h2>
        <span class="temp">16&deg;</span>
        <div class="wx" title="Zonnig" style="background-image: url('sun.png');"></div>
    </div>
</body>
</html>
"""


def test_parser_complete_extraction():
    """Verify parsing framework handles all visual markers and converts types seamlessly."""
    parser = WeerplazaParser(FULL_SAMPLE_HTML)
    data = parser.extract_data()

    assert data["rain"] == "Lichte regen"
    assert data["flash_detection"] == "Onweer gedetecteerd binnen 15km"
    assert data["flash_range"] == 15
    assert data["alerts"] == "Met waarschuwingen"

    assert data["astro"]["sun"]["rise"] == "05:45"
    assert data["astro"]["sun"]["set"] == "21:30"
    assert data["moon_phases"][0]["phase"] == "Volle maan"
    assert data["moon_phases"][0]["icon"] == "https://www.weerplaza.nl/assets/moon.png"

    assert data["hourly_forecast"][0]["time"] == "14:00"
    assert data["hourly_forecast"][0]["temperature"] == 19.0

    assert data["daily_forecast_summary"][0]["date_short"] == "Maandag 20 mei"
    assert data["daily_forecast_summary"][0]["temp_high"] == "22"
    assert data["daily_forecast_summary"][0]["temp_low"] == "11"

    assert data["current_temperature"] == 16.0
