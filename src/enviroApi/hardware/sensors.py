
import math
import json
import time
from sgp30 import SGP30
from smbus2 import SMBus
from ltr559 import LTR559
from enviroplus import gas
from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError, ChecksumMismatchError
from subprocess import check_output
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enviroApi.data import SensorData
from enviroApi.config import Config, variable_units
import logging
from subprocess import PIPE, Popen
from datetime import datetime
import dataclass

@dataclass
class Values():
    """Dataclass to hold values of sensor readings
    init:
        value (float): value of sensor reading
        timestamp (datetime): timestamp of when the value of read
        unit (str): Unit for the balues
    Returns:
        dataclass
    """

    value: float
    timestamp: datetime
    unit: str
    name: str


class Sensors():
    # TODO
    # Add some common API to this class of the following
    # SCAN_//SENSOR() -> Does the vall to the sensor
    # READ_//SENSOR_VALUE() -> reaturns the value of the sensor read
    # OBSERVE_//SENSOR() -> read and return values
    def __init__(self, config: Config, logging, variable_units: variable_units):
        # Create a BME280 instance
        self.config = config
        self.logger = logger
        self._sensor_intilization()
        self.var_unit = variable_units

    def _sensor_intilization(self):
        self._inable_cpu_temp()
        self._enable_bme280()
        self._enable_particle_sensor()
        self._enable_light_sensor()
        self._enable_ec02_vox_sensor()
        self._enable_gas_sensor()

    def _enable_cpu_temp():
        # Get the temperature of the CPU for compensation
        self.cpu_temp = Values(value = 0.00, timestamp = self.ts(), unit = 'C', name = "cpu" + self.variable_units.temperature)

    def _enable_bm280(self):
        self.bme280 = BME280(i2c_dev=SMBus(1))
        self.temperature = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.temprature_unit, name = self.variable_units.temprature) 
        self.humidiity = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.humidiity_unit, name = self.variable_units.humidiity) 
        self.pressure = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.pressure_unit, name = self.variable_units.pressure) 

    def _enable_particle_sensor(self):
        """Import sensor for use with the enviropi particle size seneor"""
        if self.config.enable_particle_sensor:
            self.pms5003 = PMS5003()
            time.sleep(1)
            self.pm1 = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.pm1_unit, name = self.variable_units.pm1) 
            self.pm2_5 = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.pm25_unit, name = self.variable_units.pm25 ) 
            self.pm10 = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.pm10_unit, name = self.variable_units.pm10) 

    def _enable_ec02_vox_sensor(self):
        if self.config.enable_eco2_tvoc
            self.spg30 = SGP30()
            self.co2 = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.co2_unit, name = self.variable_units.co2) 
            self.voc = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.voc_unit, name = self.variable_units.voc) 

    def _enable_gas_sensor(Self):
        if self.config.enable_oxi_redux_nh3:
            self.gas_sensor = gas
            self.redux = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.reducing_unit, name = self.variable_units.reducing) 
            self.oxi = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.oxidising_unit, name = self.variable_units.oxidising) 
            self.nh3 = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.nh3_unit, name = self.variable_units.nh3) 

    def _enable_light_sensor(self):
        self.ltr559 = LTR559()
        self.lux = Values(value = 0.00, timestamp = self.ts(), unit = self.variable_units.light_unit, name = self.variable_units.light) 

    def _enable_sound_sensor(self):
        pass

    def ts(self):
        return datetime.now()

    def scan_sensors(self):
        self.scan_cpu_sensor()
        self.scan_temperature_sensor()
        self.scan_pressure_sensor()
        self.scan_humidity_sensor()
        if self.config.enable_proxy_sensory:
            self.scan_light_sensor()
        if self.config.enable_oxi_redux_nh3:
            self.scan_gas_sensor()
        if self.config.enable_particle_sensor:
            self.scan_particle_sensor
        if self.config.enable_eco2_tvoc:
            self.scan_eco2_tvoc_sensor()
        if self.config.enable_noise:
            #TO DO need to implement a class to connect noise sensors
            pass
            
    def read_sensors(self):
        return_list = [self.read_cpu_sensor(), self.read_temperature_sensor(), self.read_pressure_sensor(), self.read_humiditiy_sensor()]
        if self.config.enable_proxy_sensory:
            return_list += [self.read_light_sensor()]
        if self.config.enable_oxi_redux_nh3:
            return_list += [*self.read_gas_sensor()]
        if self.config.enable_particle_sensor:
            return_list += [*self.read_particle_sensor()]
        if self.config.enable_eco2_tvoc:
            return_list += [*self.read_eco2_tvoc_sensor()]
        if self.config.enable_noise:
            pass
        return return_list
        
    def observe_sensors(self):
        self.scan_sensors()
        return self.read_sensors()

    def scan_cpu_sensor(self):
        process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
        output, _error = process.communicate()
        self.cpu_temp.value = float(output[output.index("=") + 1:output.rindex("'")])
        self.cpu_temp.ts = self.ts()

    def read_cpu_sensor(self):
        return self.cpu_temp
        
    def observe_cpu_sensor(self):
        self.scan_cpu_sensor():
        return self.read_cpu_sensor()

    def scan_light_sensor(self):
        self.lux.value = self.ltr559.get_lux()
        self.lux.timestamp = self.ts()
        
    def read_light_senor(self):
        return (self.var_unit.light ,self.lux)

    def observe_light_sensor(self):
        self.scan_light_sensor()
        return self.read_light_sensor()

    def scan_humidity_sensor(self):
        self.humiditiy.value = self.bme280.get_humidity()
        self.humiditiy.ts = self.ts()

    def read_humiditiy_sensor(self)
        return self.humidity

    def observe_humidity_sensor(self):
        self.scan_humidity_sensor()
        return self.read_humiditiy_sensor()

    def scan_temperature_sensor(self):
        self.temperature.value  = self.bme280.get_temperature()
        self.temperature.timestamp = self.ts()

    def read_temperature_sensor(self):
        return self.temperature

    def observe_temperature_sensor(self):
        self.scan_temperature_sensor()
        return self.read_temperature_sensor()

    def scan_pressure_sensor(self):
        self.pressure.value = self.bme280.get_pressure()
        self.pressure.ts = self.ts()

    def read_pressure_sensor(self):
        return self.pressure

    def observe_pressure_sensor(self):
        self.scan_pressure_sensor()
        return self.read_pressure_sensor()

    def scan_reducing_sensor(self):
        self.redux.value = round(self.gas_sensor().reducing, 0)
        self.redux.timestamp = self.ts()

    def read_reducing_sensor(self):
        return self.redux

    def observe_reducing_sensor(self):
        self.scan_reducing_sensor()
        return self.read_reducing_sensor()

    def scan_oxidising_sensor(self):
        self.oxi.value = round(self.gas_sensor().oxidising, 0)
        self.oxi.timestamp = self.ts()

    def read_oxidising_sensor(self)
        return self.oxi

    def observe_oxidising_sensor(self):
        self.scan_oxidising_sensor()
        return self.read_oxidising_sensor()
          
    def scan_nh3_sensor(self):
        self.nh3.value = round(self.gas_sensor().nh3, 0)
        self.nh3.timestamp = self.ts()

    def read_nh3_sensor(self):
        return self.nh3

    def observe_nh3_sensor(self):
        self.scan_nh3_sensor()
        return self.read_nh3_sensor()

    def scan_gas_sensor(self):
        gas_data = self.gas_sensor.read_all()
        ts = self.ts()
        self.redux.value = round(gas_data.reducing, 0)
        self.oxi.value = round(gas_data.oxidising, 0)
        self.nh3.value = round(gas_data.nh3, 0)
        self.redux.timestamp = ts
        self.oxi.timestamp = ts
        self.nh3.timestamp = ts

    def read_gas_sensor(self)
    return self.raw_red_rs, self.raw_oxi_rs, self.raw_nh3_rs

    def observe_gas_sensor(self):
        self.scan_gas_sensor()
        return self.read_gas_sensor()

    def scan_particle_sensor(self):
        if enable_particle_sensor:
            try:
                pm_values = self.bme280pms5003.read()
                ts = self.ts()
                self.pm1.value = pm_values.pm_ug_per_m3(1)
                self.pm2_5.value = pm_values.pm_ug_per_m3(2.5)
                self.pm10.value = pm_values.pm_ug_per_m3(10)
                self.pm1.timestamp = ts
                self.pm2_5.timestamp = ts
                self.pm10.timestamp = ts
            except (ReadTimeoutError, ChecksumMismatchError):
                logging.info("Failed to read PMS5003")
                display_error('Particle Sensor Error')
                self.pms5003.reset()
                pm_values = pms5003.read()
                ts = self.ts
                self.pm1.value = pm_values.pm_ug_per_m3(1)
                self.pm2_5.value = pm_values.pm_ug_per_m3(2.5)
                self.pm10.value = pm_values.pm_ug_per_m3(10)
                self.pm1.timestamp = ts
                self.pm2_5.timestamp = ts
                self.pm10.timestamp = ts


    def read_particle_sensor(self):
        return self.pm1, self.pm2_5, self.pm10

    def observe_particle_sensor(self):
        self.scan_particle_sensor()
        return self.read_particle_sensor()

    def scan_eco2_tvoc_sensor(self):
        self.co2.value, self.voc.value = self.sgp30.command('measure_air_quality')
        ts = self.ts
        self.co2.timestamp = ts
        self.voc.timestamp = ts
        
    def read_eco2_tvoc_sensor(self):
        return self.co2, self.voc

    def observe_eco2_tvoc_sensor(self):
        self.scan_eco2_tvoc_sensor()
        return self.read_eco2_tvoc_sensor()

    def scan_sound_sensor(self):
        pass

    def read_sound_sensor(self):
        pass

    def observe_sound_sensor(self):
        pass

class sensor_calculation():
    """Class that takes raw data from Sensors and converts them into somethimg meaningfull

    """
    def __init__(self, config: Config, compensation: Compensation):
        self.config = Config
        self.compensation = Compensation

    def saturation_vapor_pressure(self, temp: float) -> float:
        """Calculates the saturation vapor pressure of the current temp Saturation vapor pressure (Pws) is the equilibrium water vapor pressure in a closed chamber containing liquid water

        Args:
            temp (float): temperature, in celscius

        Return:
            saturation vapor pressure

        Source: 
            https://docs.vaisala.com/r/M211280EN-D/en-US/GUID-37BB534A-95E5-46A5-A1C3-03F4A51F879D
        """
        theta = temp - (0.49313580 * math.pow(temp, 0) + -0.0046094296 * math.pow(temp, 1) + 0.000013746454  * meth.pow(temp,2) + 
    -0.000000012743214 * math.pow(temp,3))
        svp = temp - (6 * 6.5459673 math.log(theta) + math.pow(theta, -1) * -0.58002206  * math.pow(10,-4) + math.pow(theta, 0) * 0.13914993 * 10 + math.pow(theta, 1) 
            * -0.48640239 * 0.1 + math.pow(theta, 2) * 0.41764768 * 0.0001 + math.pow(theta, 3) *  -0.14452093 * math.pow(10,-7))
        return svp
        
    def water_vapor_pressure(self, temp: float, relative_humidity: float) -> float:
        """calculate the water vapor pressures

        Args:
            temp (float): temprature in C
            relative_humidity (float): relative humidiity (in %)
            
        Returns:
            float: water vapor pressure (in hPa)

        https://en.wikipedia.org/wiki/Vapour_pressure_of_water
        """
        # the below uses the formula from  https://docs.vaisala.com/r/M211280EN-D/en-US/GUID-37BB534A-95E5-46A5-A1C3-03F4A51F879D
        # wvp = relative_humidity * self.saturation_vapor_pressure(temp)
        relative_humidity = self.relative_humidity(relative_humidity) # Just in case
        wvp = relative_humidity * 0.61121 * math.exp((18.678 - temp / 234.5) * (temp / (257.14 + temp))) * 10

        return wvp

    def relative_humidity(self, raw_humidity: float) -> float:
        """Takes the raw input from the source system (bme280) and converts it to relative humidity

        Args:
           raw_humidity (float): raw_humidity

        Returns:
            float: relative humiditity
        """
        if raw_humidity >= 1.00:
            return raw_humidity/100.0
        else:
            return raw_humidity

    def absolute_humidity(self, temp: float, relative_humidity: float) -> float:
        """Calculates the abosluate humidity (mass of water in a given volume) in g per cubic meeter

        Args:
            temp (float): temperature in C
            relative_humidity (float): relative humidiity

        Returns:
            float: Absolute Humidiity (in g / m^3)
        https://docs.vaisala.com/r/M211280EN-D/en-US/GUID-905DDD94-2974-479D-8DCD-33811A9A081B
        """
        wvp = self.water_vapor_pressure(temp, relative_humidity)
        AH = 216.679 * wvp/(temp + 273.15)
        return AH

    def mixing_ratio(self, temp: float, relative_humidity: float, pressure: float) -> float:
        """The mixing ratio (x, mass of water vapour/mass of dry gas) 

        Args:
            temp (float): temperature (in C)
            relative_humidity (float): relative humidiity
            pressure (float): pressure (in hPa)

        Returns:
            float: the ratio water vs the mass of the dry gass (g/kg)

        https://docs.vaisala.com/r/M211280EN-D/en-US/GUID-BF3EEF1B-ECEF-4B2C-AB1C-5F7DD642D24C
        """
        wvp = self.water_vapor_pressure(temp, relative_humidity)
        MR = 621.9907 * wvp / (pressure - wvp)

        return MR

    def dew_point(self, temp: float, relative_humidity: float) -> float:
        """calculates the dew point at the humidiity and temp

        Args:
            temp (float): temp in C
            relative_humidity (float): relative humidiity (between 0 and 1.00)

        Returns:
            float: dew point (in C)

        https://en.wikipedia.org/wiki/Dew_point
        """
        wvp = self.water_vapor_pressure(temp, relative_humidity)
        lmd = math.log(self.relative_humidity(relative_humidity)) + (17.625  * temp)/ (243.04 + temp)

        dp = (243.04 * lmd)/(17.625 - lmd)

        return dp

    def adjust_temperature(self, temp: float, cpu_temp: Union[float, list, None] = None, cpu_factor: float = 2.25) -> float:
        """_summary_

        Args:
            temp (float): temperature from the sensor
            cpu_temp (Union[float, list, None], optional): Temperature from the CPU. Defaults to None.
            cpu_factor (float, optional): Tuning factor for compensation. Defaults to 2.25.

        Details:
            There are two ways the math is done with this. 
                1) First, it's done via the environ+ method of balancing the temperature against the CPU temp. Use this method if the environplus board sits right
                above the cpu of the raspberrypi. the cpu_factor   is used to adjust the amount the cpu impacts the enviornplus temp sensor
                Decrease the cpu_factor to adjust the temperature down, and increase to adjust up.
                2) Regression testing (from https://github.com/roscoe81/enviro-monitor). Some dude (probably roscoe81) took a ton of readings, then fit a cubic line
                of best fit to get the right temperature adjustments. Use this method if your temperature sensor doesn't sit close to the raspberrypi cpu
    
        Returns:
            float: returns the adjust temperature, based on the above. 
        """
        if use_cpu:
            adjusted_temperature = temp - ((cpu_temp - temp) / cpu_factor)
        else:
            adjusted_temperature = (self.compensation.comp_temp_cub_a * math.pow(temp, 3) + self.compensation.comp_temp_cub_b * math.pow(temp, 2) +
                 self.compensation.comp_temp_cub_c * temp + self.compensation.comp_temp_cub_d)
        return adjusted_temperature

# Read gas and climate values from Home Manager and /or BME280 
def read_climate_gas_values(luft_values, mqtt_values, own_data, maxi_temp, mini_temp, own_disp_values, gas_sensors_warm,
                            gas_calib_temp, gas_calib_hum, gas_calib_bar, altitude, enable_eco2_tvoc):
    raw_temp, comp_temp = adjusted_temperature()
    raw_hum, comp_hum = adjusted_humidity()
    current_time = time.time()
    use_external_temp_hum = False
    use_external_barometer = False
    if enable_receive_data_from_homemanager:
        use_external_temp_hum, use_external_barometer = es.check_valid_readings(current_time)
    if use_external_temp_hum == False:
        print("Internal Temp/Hum Sensor")
        luft_values["temperature"] = "{:.2f}".format(comp_temp)
        own_data["Temp"][1] = round(comp_temp, 1)
        luft_values["humidity"] = "{:.2f}".format(comp_hum)
        own_data["Hum"][1] = round(comp_hum, 1)
    else: # Use external temp/hum sensor but still capture raw temp and raw hum for gas compensation and logging
        print("External Temp/Hum Sensor")
        luft_values["temperature"] = es.temperature
        own_data["Temp"][1] = float(luft_values["temperature"])
        luft_values["humidity"] = es.humidity
        own_data["Hum"][1] = float(luft_values["humidity"])

    own_data["Dew"][1] = round(calculate_dewpoint(own_data["Temp"][1], own_data["Hum"][1]),1)
    own_disp_values["Dew"] = own_disp_values["Dew"][1:] + [[own_data["Dew"][1], 1]]
    mqtt_values["Dew"]  = own_data["Dew"][1]
    own_disp_values["Temp"] = own_disp_values["Temp"][1:] + [[own_data["Temp"][1], 1]]
    mqtt_values["Temp"] = own_data["Temp"][1]
    own_disp_values["Hum"] = own_disp_values["Hum"][1:] + [[own_data["Hum"][1], 1]]
    mqtt_values["Hum"][0] = own_data["Hum"][1]
    mqtt_values["Hum"][1] = domoticz_hum_map[describe_humidity(own_data["Hum"][1])]
    if enable_eco2_tvoc: # Calculate and send the absolute humidity reading to the SGP30 for humidity compensation
        absolute_hum = int(1000 * 216.7 * (raw_hum/100 * 6.112 * math.exp(17.62 * raw_temp / (243.12 + raw_temp)))
                           /(273.15 + raw_temp))
        sgp30.command('set_humidity', [absolute_hum])
    else:
        absolute_hum = None
    # Determine max and min temps
    if first_climate_reading_done :
        if maxi_temp is None:
            maxi_temp = own_data["Temp"][1]
        elif own_data["Temp"][1] > maxi_temp:
            maxi_temp = own_data["Temp"][1]
        else:
            pass
        if mini_temp is None:
            mini_temp = own_data["Temp"][1]
        elif own_data["Temp"][1] < mini_temp:
            mini_temp = own_data["Temp"][1]
        else:
            pass
    mqtt_values["Min Temp"] = mini_temp
    mqtt_values["Max Temp"] = maxi_temp
    raw_barometer = bme280.get_pressure()
    if use_external_barometer == False:
        print("Internal Barometer")
        own_data["Bar"][1] = round(raw_barometer * barometer_altitude_comp_factor(altitude, own_data["Temp"][1]), 2)
        own_disp_values["Bar"] = own_disp_values["Bar"][1:] + [[own_data["Bar"][1], 1]]
        mqtt_values["Bar"][0] = own_data["Bar"][1]
        luft_values["pressure"] = "{:.2f}".format(raw_barometer * 100) # Send raw air pressure to Lufdaten,
        # since it does its own altitude air pressure compensation
        print("Raw Bar:", round(raw_barometer, 2), "Comp Bar:", own_data["Bar"][1])
    else:
        print("External Barometer")
        own_data["Bar"][1] = round(float(es.barometer), 2)
        own_disp_values["Bar"] = own_disp_values["Bar"][1:] + [[own_data["Bar"][1], 1]]
        mqtt_values["Bar"][0] = own_data["Bar"][1]
        # Remove altitude compensation from external barometer because Lufdaten does its own altitude air pressure
        # compensation
        luft_values["pressure"] = "{:.2f}".format(float(es.barometer) / barometer_altitude_comp_factor (
            altitude, own_data["Temp"][1]) * 100)
        print("Luft Bar:", luft_values["pressure"], "Comp Bar:", own_data["Bar"][1])
    red_in_ppm, oxi_in_ppm, nh3_in_ppm, comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs =\
        read_gas_in_ppm(gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer, gas_sensors_warm)
    own_data["Red"][1] = round(red_in_ppm, 2)
    own_disp_values["Red"] = own_disp_values["Red"][1:] + [[own_data["Red"][1], 1]]
    mqtt_values["Red"] = own_data["Red"][1]
    own_data["Oxi"][1] = round(oxi_in_ppm, 2)
    own_disp_values["Oxi"] = own_disp_values["Oxi"][1:] + [[own_data["Oxi"][1], 1]]
    mqtt_values["Oxi"] = own_data["Oxi"][1]
    own_data["NH3"][1] = round(nh3_in_ppm, 2)
    own_disp_values["NH3"] = own_disp_values["NH3"][1:] + [[own_data["NH3"][1], 1]]
    mqtt_values["NH3"] = own_data["NH3"][1]
    mqtt_values["Gas Calibrated"] = gas_sensors_warm
    proximity = ltr559.get_proximity()
    if proximity < 500:
        own_data["Lux"][1] = round(ltr559.get_lux(), 1)
    else:
        own_data["Lux"][1] = 1
    own_disp_values["Lux"] = own_disp_values["Lux"][1:] + [[own_data["Lux"][1], 1]]
    mqtt_values["Lux"] = own_data["Lux"][1]
    return luft_values, mqtt_values, own_data, maxi_temp, mini_temp, own_disp_values, raw_red_rs, raw_oxi_rs,\
           raw_nh3_rs, raw_temp, comp_temp, comp_hum, raw_hum, use_external_temp_hum, use_external_barometer,\
           raw_barometer, absolute_hum
    
def barometer_altitude_comp_factor(alt, temp):
    comp_factor = math.pow(1 - (0.0065 * altitude/(temp + 0.0065 * alt + 273.15)), -5.257)
    return comp_factor
    

    
def read_gas_in_ppm(gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer, gas_sensors_warm):
    if gas_sensors_warm:
        comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs = comp_gas(gas_calib_temp,
                                                                                             gas_calib_hum,
                                                                                             gas_calib_bar,
                                                                                             raw_temp,
                                                                                             raw_hum, raw_barometer)
        print("Reading Compensated Gas sensors after warmup completed")
    else:
        raw_red_rs, raw_oxi_rs, raw_nh3_rs = read_raw_gas()
        comp_red_rs = raw_red_rs
        comp_oxi_rs = raw_oxi_rs
        comp_nh3_rs = raw_nh3_rs
        print("Reading Raw Gas sensors before warmup completed")
    print("Red Rs:", round(comp_red_rs, 0), "Oxi Rs:", round(comp_oxi_rs, 0), "NH3 Rs:", round(comp_nh3_rs, 0))
    if comp_red_rs/red_r0 > 0:
        red_ratio = comp_red_rs/red_r0
    else:
        red_ratio = 0.0001
    if comp_oxi_rs/oxi_r0 > 0:
        oxi_ratio = comp_oxi_rs/oxi_r0
    else:
        oxi_ratio = 0.0001
    if comp_nh3_rs/nh3_r0 > 0:
        nh3_ratio = comp_nh3_rs/nh3_r0
    else:
        nh3_ratio = 0.0001
    red_in_ppm = math.pow(10, -1.25 * math.log10(red_ratio) + 0.64)
    oxi_in_ppm = math.pow(10, math.log10(oxi_ratio) - 0.8129)
    nh3_in_ppm = math.pow(10, -1.8 * math.log10(nh3_ratio) - 0.163)
    return red_in_ppm, oxi_in_ppm, nh3_in_ppm, comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs

def comp_gas(gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer):
    gas_data = gas.read_all()
    gas_temp_diff = raw_temp - gas_calib_temp
    gas_hum_diff = raw_hum - gas_calib_hum
    gas_bar_diff = raw_barometer - gas_calib_bar
    raw_red_rs = round(gas_data.reducing, 0)
    comp_red_rs = round(raw_red_rs - (red_temp_comp_factor * raw_red_rs * gas_temp_diff +
                                      red_hum_comp_factor * raw_red_rs * gas_hum_diff +
                                      red_bar_comp_factor * raw_red_rs * gas_bar_diff), 0)
    raw_oxi_rs = round(gas_data.oxidising, 0)
    comp_oxi_rs = round(raw_oxi_rs - (oxi_temp_comp_factor * raw_oxi_rs * gas_temp_diff +
                                      oxi_hum_comp_factor * raw_oxi_rs * gas_hum_diff +
                                      oxi_bar_comp_factor * raw_oxi_rs * gas_bar_diff), 0)
    raw_nh3_rs = round(gas_data.nh3, 0)
    comp_nh3_rs = round(raw_nh3_rs - (nh3_temp_comp_factor * raw_nh3_rs * gas_temp_diff +
                                      nh3_hum_comp_factor * raw_nh3_rs * gas_hum_diff +
                                      nh3_bar_comp_factor * raw_nh3_rs * gas_bar_diff), 0)
    print("Gas Compensation. Raw Red Rs:", raw_red_rs, "Comp Red Rs:", comp_red_rs, "Raw Oxi Rs:",
          raw_oxi_rs, "Comp Oxi Rs:", comp_oxi_rs,
          "Raw NH3 Rs:", raw_nh3_rs, "Comp NH3 Rs:", comp_nh3_rs)
    return comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs   
    
def adjusted_temperature():
    raw_temp = bme280.get_temperature()
    #comp_temp = comp_temp_slope * raw_temp + comp_temp_intercept
    comp_temp = (comp_temp_cub_a * math.pow(raw_temp, 3) + comp_temp_cub_b * math.pow(raw_temp, 2) +
                 comp_temp_cub_c * raw_temp + comp_temp_cub_d)
    return raw_temp, comp_temp

def adjusted_humidity():
    raw_hum = bme280.get_humidity()
    #comp_hum = comp_hum_slope * raw_hum + comp_hum_intercept
    comp_hum = comp_hum_quad_a * math.pow(raw_hum, 2) + comp_hum_quad_b * raw_hum + comp_hum_quad_c
    return raw_hum, min(100, comp_hum)

def calculate_dewpoint(dew_temp, dew_hum):
    dewpoint = (237.7 * (math.log(dew_hum/100)+17.271*dew_temp/(237.7+dew_temp))/(17.271 - math.log(dew_hum/100) - 17.271*dew_temp/(237.7 + dew_temp)))
    return dewpoint

def log_climate_and_gas(run_time, own_data, raw_red_rs, raw_oxi_rs, raw_nh3_rs, raw_temp, comp_temp, comp_hum,
                        raw_hum, use_external_temp_hum, use_external_barometer, raw_barometer):
    # Used to log climate and gas data to create compensation algorithms
    raw_temp = round(raw_temp, 2)
    raw_hum = round(raw_hum, 2)
    comp_temp = round(comp_temp, 2)
    comp_hum = round(comp_hum, 2)
    raw_barometer = round(raw_barometer, 1)
    raw_red_rs = round(raw_red_rs, 0)
    raw_oxi_rs = round(raw_oxi_rs, 0)
    raw_nh3_rs = round(raw_nh3_rs, 0)
    today = datetime.now()
    time_stamp = today.strftime('%A %d %B %Y @ %H:%M:%S')
    if use_external_temp_hum and use_external_barometer:
        environment_log_data = {'Time': time_stamp, 'Run Time': run_time, 'Raw Temperature': raw_temp,
                                'Output Temp': comp_temp, 'Real Temperature': own_data["Temp"][1],
                                'Raw Humidity': raw_hum, 'Output Humidity': comp_hum,
                                'Real Humidity': own_data["Hum"][1], 'Real Bar': own_data["Bar"][1],
                                'Raw Bar': raw_barometer, 'Oxi': own_data["Oxi"][1], 'Red': own_data["Red"][1],
                                'NH3': own_data["NH3"][1], 'Raw OxiRS': raw_oxi_rs, 'Raw RedRS': raw_red_rs,
                                'Raw NH3RS': raw_nh3_rs}
    elif use_external_temp_hum and not(use_external_barometer):
        environment_log_data = {'Time': time_stamp, 'Run Time': run_time, 'Raw Temperature': raw_temp,
                                'Output Temp': comp_temp, 'Real Temperature': own_data["Temp"][1],
                                'Raw Humidity': raw_hum, 'Output Humidity': comp_hum,
                                'Real Humidity': own_data["Hum"][1], 'Output Bar': own_data["Bar"][1],
                                'Raw Bar': raw_barometer, 'Oxi': own_data["Oxi"][1], 'Red': own_data["Red"][1],
                                'NH3': own_data["NH3"][1], 'Raw OxiRS': raw_oxi_rs, 'Raw RedRS': raw_red_rs,
                                'Raw NH3RS': raw_nh3_rs}
    elif not(use_external_temp_hum) and use_external_barometer:
        environment_log_data = {'Time': time_stamp, 'Run Time': run_time, 'Raw Temperature': raw_temp,
                                'Output Temp': comp_temp, 'Raw Humidity': raw_hum, 'Output Humidity': comp_hum,
                                'Real Bar': own_data["Bar"][1], 'Raw Bar': raw_barometer, 'Oxi': own_data["Oxi"][1],
                                'Red': own_data["Red"][1], 'NH3': own_data["NH3"][1], 'Raw OxiRS': raw_oxi_rs,
                                'Raw RedRS': raw_red_rs, 'Raw NH3RS': raw_nh3_rs}
    else:
        environment_log_data = {'Time': time_stamp, 'Run Time': run_time, 'Raw Temperature': raw_temp,
                                'Output Temp': comp_temp,  'Raw Humidity': raw_hum, 'Output Humidity': comp_hum,
                                'Output Bar': own_data["Bar"][1], 'Raw Bar': raw_barometer, 'Oxi': own_data["Oxi"][1],
                                'Red': own_data["Red"][1], 'NH3': own_data["NH3"][1], 'Raw OxiRS': raw_oxi_rs,
                                'Raw RedRS': raw_red_rs, 'Raw NH3RS': raw_nh3_rs}
    print('Logging Environment Data.', environment_log_data)
    with open('<Your Environment Log File Location Here>', 'a') as f:
        f.write(',\n' + json.dumps(environment_log_data))
    
# Calculate Air Quality Level
def max_aqi_level_factor(gas_sensors_warm, air_quality_data, air_quality_data_no_gas, data):
    max_aqi_level = 0
    max_aqi_factor = 'All'
    max_aqi = [max_aqi_factor, max_aqi_level]
    if gas_sensors_warm:
        aqi_data = air_quality_data
    else:
        aqi_data = air_quality_data_no_gas
    for aqi_factor in aqi_data:
        aqi_factor_level = 0
        thresholds = data[aqi_factor][2]
        for level in range(len(thresholds)):
            if data[aqi_factor][1] != None:
                if data[aqi_factor][1] > thresholds[level]:
                    aqi_factor_level = level + 1
        if aqi_factor_level > max_aqi[1]:
            max_aqi = [aqi_factor, aqi_factor_level]
    return max_aqi
        