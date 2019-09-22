#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

root_path = os.path.dirname(os.path.abspath(__file__))

config = {
    "separator": "####",
    "elasticsearch-index": "cadaster",
    "error_log_file": os.path.join(root_path, 'logs', 'log'),
    "tracking_log_file": os.path.join(root_path, 'logs', 'track'),
    "scale": 10000,
    "coordinates_path": os.path.join(root_path, 'coordinates'),
    "not_available_via_XML": "(Not available via XML)",
    "sleep_time": 5,
    "sleep_dos_time": 300,
    "width_px": 120,
    "height_px": 120,
    "servers_down_message_001": "Error 001: Cadastro server to get provinces and cities is down.\n"
                                "Consequence: Search by provinces will fail.\n"
                                "Maintenance is usually carried out durign the night or the weekends. Please, retry later.\n"
                                "As an alternative, your IP address may have been banned. Try to change your public IP",
    "servers_down_message_002": "Error 002: Cadastro server to query by cadaster number is off.\n"
                                "Search by Coordinates will fail.\n"
                                "Maintenance is usually carried out durign the night or the weekends. Please, retry later.\n"
                                "As an alternative, your IP address may have been banned. Try to change your public IP\n"

}
