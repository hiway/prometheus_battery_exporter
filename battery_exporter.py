#!/usr/bin/python
import time

import power
from flask import Flask, Response

app = Flask(__name__)

PROMETHEUS_METRICS_TEMPLATE = '''\
# HELP power_source_type Power source type: 1: AC, 2: UPS, 3: Battery.
# TYPE power_source_type gauge
power_source_type {power_source_type}

# HELP power_remaining_estimate_seconds: -2: Unlimited, -1: Unknown, seconds remaining otherwise. 
# TYPE power_warning_level gauge
power_warning_level {power_warning_level}

# HELP power_warning_level Power warning level: 1: None, 2: Early (<22% battery), 3: Final (< 10 min).
# TYPE power_remaining_estimate_seconds gauge
power_remaining_estimate_seconds {power_remaining_estimate}
'''

POWER_TYPE_MAP = {
    power.POWER_TYPE_AC: 1,
    power.POWER_TYPE_UPS: 2,
    power.POWER_TYPE_BATTERY: 3,
}

POWER_WARNING_LEVEL_MAP = {
    power.LOW_BATTERY_WARNING_NONE: 1,
    power.LOW_BATTERY_WARNING_EARLY: 2,
    power.LOW_BATTERY_WARNING_FINAL: 3,
}


def power_source_type():
    power_type = power.PowerManagement().get_providing_power_source_type()
    return POWER_TYPE_MAP[power_type]


def power_remaining_estimate():
    return power.PowerManagement().get_time_remaining_estimate()


def power_warning_level():
    level = power.PowerManagement().get_low_battery_warning_level()
    return POWER_WARNING_LEVEL_MAP[level]


@app.route('/metrics')
def metrics():
    response = PROMETHEUS_METRICS_TEMPLATE.format(
        power_warning_level=power_warning_level(),
        power_remaining_estimate=power_remaining_estimate(),
        power_source_type=power_source_type(),
        timestamp=int(time.time()),
    )
    return Response(response, mimetype='text/plain')


app.run(host='0.0.0.0', port=9199)
