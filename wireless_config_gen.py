import config


def gen_device(device_name, options=None):
    # Default device options
    device = config.default_device_config
    device["wifi-device"] = device_name

    # Change default device values if set in options
    if options is not None:
        if 'type' in options:
            device["type"] = options["type"]
        if 'hwmode' in options:
            device["hwmode"] = options["hwmode"]
        if 'path' in options:
            device["path"] = options["path"]
        if 'country' in options:
            device["country"] = options["country"]
        if 'legacy_rates' in options:
            device["legacy_rates"] = options["legacy_rates"]
        if 'channel' in options:
            device["channel"] = options["channel"]
        if 'htmode' in options:
            device["htmode"] = options["htmode"]

    device_config = (
        "config 'wifi-device' '"+device["wifi-device"]+"'\n"
        "        option 'type' '"+device["type"]+"'\n"
        "        option 'hwmode' '"+device["hwmode"]+"'\n"
        "        option 'path' '"+device["path"]+"'\n"
        "        option 'country' '"+device["country"]+"'\n"
        "        option 'legacy_rates' '"+device["legacy_rates"]+"'\n"
        "        option 'channel' '"+device["channel"]+"'\n"
        "        option 'htmode' '"+device["htmode"]+"'\n"
    )

    return device_config


def gen_iface(device_name, options=None):
    # Default interface options
    iface = config.default_iface_config
    iface["wifi-iface"] = "default_"+device_name
    iface["device"] = device_name

    # Change default iface values if set in options
    if options is not None:
        if 'wifi-iface' in options:
            iface["wifi-iface"] = filter(str.isalnum, options["wifi-iface"].lower())
        if 'device' in options:
            iface["device"] = options["device"]
        if 'network' in options:
            iface["network"] = options["network"]
        if 'mode' in options:
            iface["mode"] = options["mode"]
        if 'ssid' in options:
            iface["ssid"] = options["ssid"]
        if 'encryption' in options:
            iface["encryption"] = options["encryption"]
        if 'wpa_psk_file' in options:
            iface["wpa_psk_file"] = options["wpa_psk_file"]
        if 'isolate' in options:
            iface["isolate"] = options["isolate"]

    # Add all options to config block
    iface_config = (
        "config 'wifi-iface' '"+iface["wifi-iface"]+"'\n"
        "        option 'device' '"+iface["device"]+"'\n"
        "        option 'network' '"+iface["network"]+"'\n"
        "        option 'mode' '"+iface["mode"]+"'\n"
        "        option 'ssid' '"+iface["ssid"]+"'\n"
        "        option 'encryption' '"+iface["encryption"]+"'\n"
        "        option 'wpa_psk_file' '"+iface["wpa_psk_file"]+"'\n"
        "        option 'isolate' '" + iface["isolate"] + "'\n"
        )

    # Return the config block
    return iface_config
