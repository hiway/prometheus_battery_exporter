#!/usr/bin/python
import time

import power
from flask import Flask, Response

app = Flask(__name__)

PROMETHEUS_METRICS_TEMPLATE = '''\
# HELP power_source_type Power source type: -10: AC, -11: UPS, -12: Battery.
# TYPE power_source_type gauge
power_source_type {power_source_type}

# HELP power_warning_level Power warning level: -20: None, -21: Early (<22% battery), -22: Final (< 10 min).
# TYPE power_warning_level gauge
power_warning_level {power_warning_level}

# HELP power_remaining_estimate_seconds: -2: Unlimited, -1: Unknown, seconds remaining otherwise. 
# TYPE power_remaining_estimate_seconds gauge
power_remaining_estimate_seconds {power_remaining_estimate}
'''

POWER_TYPE_MAP = {
    power.POWER_TYPE_AC: -10,
    power.POWER_TYPE_UPS: -11,
    power.POWER_TYPE_BATTERY: -12,
}

POWER_WARNING_LEVEL_MAP = {
    power.LOW_BATTERY_WARNING_NONE: -20,
    power.LOW_BATTERY_WARNING_EARLY: -21,
    power.LOW_BATTERY_WARNING_FINAL: -22,
}


def power_source_type():
    power_type = power.PowerManagement().get_providing_power_source_type()
    return POWER_TYPE_MAP[power_type]


def power_remaining_estimate():
    estimate = power.PowerManagement().get_time_remaining_estimate()
    if estimate < 0:
        return estimate
    # API returns minutes, Prometheus prefers seconds as the standard.
    return estimate * 60


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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', default='0.0.0.0')
    parser.add_argument('-p', '--port', default='9199')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
