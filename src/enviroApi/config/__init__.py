import os
import json
import importlib.resources as ilr
from typing import Union
from dataclass import dataclass


@dataclass
class Config(frozen=True):
    c_or_f: str = "C"
    temp_offset: Union[float, int] = 0.0
    altitude: int = 0
    enable_display: bool
    compensation_path: str
    enable_proxy_Sensors: bool
    enable_climate_and_gas_logging: bool
    enable_particle_sensor: bool
    enable_oxi_redux_nh3: bool
    enable_eco2_tvoc: bool
    gas_daily_r0_calibration_hour: int
    reset_gas_sensor_calibration: bool
    enable_noise: bool
    has_weather_cover: bool
    city_name: str
    time_zone: str


@dataclass
class Variable_units:
    # TO DO need to check the units for cos and voc
    variables: list = [
        "light",
        "temperature",
        "pressure",
        "humidity",
        "oxi",
        "redux",
        "nh3",
        "pm1",
        "pm2.5",
        "pm10",
        "noise",
        "c02",
        "voc",
    ]
    units: list = [
        "Lux",
        "C",
        "hPa",
        "%",
        "kOhms",
        "kOhms",
        "kOhms",
        "ug/m3",
        "ug/m3",
        "ug/m3",
        "dBa",
        "kOhms",
        "kOhms",
    ]
    light: str = variables[0]
    light_unit: str = units[0]
    temperature: str = variables[1]
    temperature_unit: str = units[1]
    pressure: str = variables[2]
    pressure_unit: str = units[2]
    humidity: str = variables[3]
    humidity_unit: str = units[3]
    oxidising: str = variables[4]
    oxidising_unit: str = units[4]
    reducing: str = variables[5]
    reducing_unit: str = units[5]
    nh3: str = variables[6]
    nh3_unit: str = units[6]
    pm1: str = variables[7]
    pm1_unit: str = units[7]
    pm25: str = variables[8]
    pm25_unit: str = units[8]
    pm10: str = variables[9]
    pm10_unit: str = units[9]
    noise: str = variables[10]
    noise_unit: str = units[10]
    co2: str = variables[11]
    co2_unit: str = units[11]
    voc: str = variables[12]
    voc_unit: str = units[12]


@dataclass
class Compensation:
    # Set temp and hum compensation when display is enabled (no weather
    # protection cover in place) and no ECO2 or TVOC sensor is in place
    # Cubic polynomial temp comp coefficients adjusted by config's temp_offset
    temp_offset: float
    comp_temp_cub_a: float
    comp_temp_cub_b: float
    comp_temp_cub_c: float
    comp_temp_cub_d: float  # note in the original logic, comp_temp_cub_d was also recast to comp_temp_dub_d + temp_offset cause Reasonssss?????
    # Quadratic polynomial hum comp coefficients
    comp_hum_quad_a: float
    comp_hum_quad_b: float
    comp_hum_quad_c: float
    # New Gas Comp Factors based on long term regression testing and proportion of RS
    red_temp_comp_factor: float
    red_hum_comp_factor: float
    red_bar_comp_factor: float
    oxi_temp_comp_factor: float
    oxi_hum_comp_factor: float
    oxi_bar_comp_factor: float
    nh3_temp_comp_factor: float
    nh3_hum_comp_factor: float
    nh3_bar_comp_factor: float


def load_compensation(config: Config, path: [str, None]) -> dataclass:
    """Loads compensation factors from file or json

    Args:
        path (str): path to config file
        config (Config): A Configuration

    Returns:
        dataclass: returns a compensation dataclass
    """
    if path is None:
        path = Config.compensation_path

    if os.path.exists(path):
        with open(os.path(path), "r") as f:
            comp_json = json.loads(f.read())
            print("Retrieved Config", config)
    else:
        with ilr.open_text("enviroApi", "compensation.json") as file:
            comp_json = json.load(file)

    weather_dict = comp_json.pop("weather")[Config.has_weather_cover].copy()

    if Config.has_weather_cover is False:
        weather_dict = weather_dict["enable_eco2_tvoc"][Config.enable_eco2_tvoc]
        weather_dict["comp_temp_cub_d"] = (
            weather_dict["comp_temp_cub_d"] + Config.Offset
        )  # Don't ask me why he does this

    compensation_dict = weather_dict | comp_json
    Comp_Class = Compensation(**compensation_dict)
    return Comp_Class


def retrieve_config(config_path: [str, None]) -> dataclass:
    """loads a config file from a json

    Args:
        config_path (str): path to json that holds the config file. If None, will load the default JSON value.

    Returns:
        returns a dataclass with the config as attributes
    """

    if os.path.exists(config_path):
        with open(os.path(config_path), "r") as f:
            config = json.loads(f.read())
            print("Retrieved Config", config)
    else:
        with ilr.open_text("enviroApi", "config.json") as file:
            config_json = json.load(file)
    config_dict = {}
    config_dict["c_or_f"] = config_json["celsius_or_fahrenheit"]
    config_dict["temp_offset"] = config_json["temp_offset"]
    config_dict["altitude"] = config_json["altitude"]
    config_dict["enable_display"] = config_json[
        "enable_display"
    ]  # Enables the display and flags
    config_dict["enable_proxy_sensor"] = config_json.get("enable_proxy_sensor", False)
    # that the weather protection cover is used with different temp/hum compensation
    config_dict["enable_climate_and_gas_logging"] = config_json[
        "enable_climate_and_gas_logging"
    ]
    config_dict["enable_particle_sensor"] = config_json["enable_particle_sensor"]
    config_dict["enable_oxi_redux_nh3"] = config_json["enable_oxi_redux_nh3"]
    config_dict["enable_eco2_tvoc"] = config_json.get("enable_eco2_tvoc", False)
    config_dict["gas_daily_r0_calibration_hour"] = config_json.get(
        "gas_daily_r0_calibration_hour", 3
    )
    config_dict["reset_gas_sensor_calibration"] = config_json.get(
        "reset_gas_sensor_calibration", False
    )
    config_dict["enable_noise"] = config_json.get("enable_noise", False)
    config_dict["compensation_path"] = config_json.get("compensation_path", "")
    config_dict["has_weather_cover"] = config_json.get("has_weather_cover", False)
    config_dict["city_name"] = config_json["city_name"]
    config_dict["time_zone"] = config_json["time_zone"]

    Config_dc = Config(**config_dict)

    return Config_dc
