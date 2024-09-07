from sgp30 import SGP30
from smbus2 import SMBus
from ltr559 import LTR559
from enviroplus import gas
from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError, ChecksumMismatchError
from enviroApi.config import Config, Variable_Units
from enviroApi.data import SensorData, Values
import logging
from subprocess import PIPE, Popen


class Sensors:
    def __init__(
        self,
        config: Config,
        log: logging,
        variable_units=Variable_Units(),
        SensorData: SensorData = SensorData(),
    ):
        # Create a BME280 instance
        self.config = config
        self.logger = log
        self._sensor_intilization()
        self.var_unit = variable_units
        self.Data = SensorData

    def _sensor_intilization(self):
        self._inable_cpu_temp()
        self._enable_bme280()
        self._enable_particle_sensor()
        self._enable_light_sensor()
        self._enable_ec02_vox_sensor()
        self._enable_gas_sensor()

    def _enable_cpu_temp(self):
        # Get the temperature of the CPU for compensation
        self.cpu_temp = Values(
            value=0.00,
            timestamp=self.ts(),
            unit="C",
            name="cpu" + self.variable_units.temperature,
        )

    def _enable_bm280(self):
        self.bme280 = BME280(i2c_dev=SMBus(1))
        self.temperature = Values(
            value=0.00,
            timestamp=self.ts(),
            unit=self.variable_units.temprature_unit,
            name=self.variable_units.temprature,
        )
        self.humidiity = Values(
            value=0.00,
            timestamp=self.ts(),
            unit=self.variable_units.humidiity_unit,
            name=self.variable_units.humidiity,
        )
        self.pressure = Values(
            value=0.00,
            timestamp=self.ts(),
            unit=self.variable_units.pressure_unit,
            name=self.variable_units.pressure,
        )

    def _enable_particle_sensor(self):
        """Import sensor for use with the enviropi particle size seneor"""
        if self.config.enable_particle_sensor:
            self.pms5003 = PMS5003()
            self.pm1 = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.pm1_unit,
                name=self.variable_units.pm1,
            )
            self.pm2_5 = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.pm25_unit,
                name=self.variable_units.pm25,
            )
            self.pm10 = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.pm10_unit,
                name=self.variable_units.pm10,
            )

    def _enable_ec02_vox_sensor(self):
        if self.config.enable_eco2_tvoc:
            self.spg30 = SGP30()
            self.co2 = Values(
                value=0.00,
                tiemestamp=self.ts(),
                unit=self.variable_units.co2_unit,
                name=self.variable_units.co2,
            )
            self.voc = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.voc_unit,
                name=self.variable_units.voc,
            )

    def _enable_gas_sensor(self):
        if self.config.enable_oxi_redux_nh3:
            self.gas_sensor = gas
            self.redux = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.reducing_unit,
                name=self.variable_units.reducing,
            )
            self.oxi = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.oxidising_unit,
                name=self.variable_units.oxidising,
            )
            self.nh3 = Values(
                value=0.00,
                timestamp=self.ts(),
                unit=self.variable_units.nh3_unit,
                name=self.variable_units.nh3,
            )

    def _enable_light_sensor(self):
        self.ltr559 = LTR559()
        self.lux = Values(
            value=0.00,
            timestamp=self.ts(),
            unit=self.variable_units.light_unit,
            name=self.variable_units.light,
        )

    def _enable_sound_sensor(self):
        pass

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
            # TO DO need to implement a class to connect noise sensors
            pass

    def read_sensors(self):
        return_list = [
            self.read_cpu_sensor(),
            self.read_temperature_sensor(),
            self.read_pressure_sensor(),
            self.read_humiditiy_sensor(),
        ]
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
        process = Popen(
            ["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True
        )
        output, _error = process.communicate()
        start_ind = output.index("=") + 1
        end_ind = output.rindex("'")
        self.cpu_temp.value = float(output[start_ind:end_ind])
        self.cpu_temp.ts = self.ts()

    def read_cpu_sensor(self):
        return self.cpu_temp

    def observe_cpu_sensor(self):
        self.scan_cpu_sensor()
        return self.read_cpu_sensor()

    def scan_light_sensor(self):
        self.lux.value = self.ltr559.get_lux()
        self.lux.timestamp = self.ts()

    def read_light_senor(self):
        return (self.var_unit.light, self.lux)

    def observe_light_sensor(self):
        self.scan_light_sensor()
        return self.read_light_sensor()

    def scan_humidity_sensor(self):
        self.humiditiy.value = self.bme280.get_humidity()
        self.humiditiy.ts = self.ts()

    def read_humiditiy_sensor(self):
        return self.humidity

    def observe_humidity_sensor(self):
        self.scan_humidity_sensor()
        return self.read_humiditiy_sensor()

    def scan_temperature_sensor(self):
        self.temperature.value = self.bme280.get_temperature()
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

    def read_oxidising_sensor(self):
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

    def read_gas_sensor(self):
        return self.raw_red_rs, self.raw_oxi_rs, self.raw_nh3_rs

    def observe_gas_sensor(self):
        self.scan_gas_sensor()
        return self.read_gas_sensor()

    def scan_particle_sensor(self):
        if self.enable_particle_sensor:
            try:
                pm_values = self.pms5003.read()
                ts = self.ts()
                self.pm1.value = pm_values.pm_ug_per_m3(1)
                self.pm2_5.value = pm_values.pm_ug_per_m3(2.5)
                self.pm10.value = pm_values.pm_ug_per_m3(10)
                self.pm1.timestamp = ts
                self.pm2_5.timestamp = ts
                self.pm10.timestamp = ts
            except (ReadTimeoutError, ChecksumMismatchError):
                # logging.info("Failed to read PMS5003")
                # display_error("Particle Sensor Error")
                self.pms5003.reset()
                pm_values = self.pms5003.read()
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
        self.co2.value, self.voc.value = self.sgp30.command("measure_air_quality")
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
