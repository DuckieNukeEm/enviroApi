import os
import json
import importlib.resources as lr


def retrieve_config(config_path: str) -> tuple:
   
    
    if os.path.exists(path_to_file):
        with open(os.path(config_path), 'r') as f:
            config = json.loads(f.read())
            print('Retrieved Config', config)
    else:
        with lr.open_text("enviroApi", "config.json") as file:
            config = json.load(file)  

    c_or_f = config['celsius_or_fahrenheit']
    temp_offset = config['temp_offset']
    altitude = config['altitude']
    enable_display = config['enable_display'] # Enables the display and flags
    # that the weather protection cover is used with different temp/hum compensation
    enable_climate_and_gas_logging = config['enable_climate_and_gas_logging']
    enable_particle_sensor = config['enable_particle_sensor']

    enable_eco2_tvoc = config.get('enable_eco2_tvoc',False)
    gas_daily_r0_calibration_hour = config.get('gas_daily_r0_calibration_hour', 3)
    reset_gas_sensor_calibration = config.get('reset_gas_sensor_calibration', False)
    enable_noise = config.get('enable_noise', False)
   
    city_name = config['city_name']
    time_zone = config['time_zone']

    return (c_or_f, temp_offset, altitude, enable_display, enable_noise, enable_climate_and_gas_logging, enable_particle_sensor,
            enable_eco2_tvoc, gas_daily_r0_calibration_hour, reset_gas_sensor_calibration, city_name, time_zone)
