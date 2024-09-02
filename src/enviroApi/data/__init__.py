from enviroApi.config import variable_units


class SensorData():
    """Class to hold data from sensors as well as historical data

    """

    def __init__(limit_history = 604800, history_check = 10000, history_remove_amt = 86400, var_untits = variable_units ):
        self.var_units = variable_units
        self.ticker = 0
        self.history_check = history_check
        self.limit_history = limit_history
        self.chunk = history_remove_amt

    def set_attributes(self):
        for K in self.var_units.variables:
            setattr(self, K, 0)
            setattr(self, K + '_hist', [])

    def add_history(self, sensor, data):
        setattr(self, sensor, getattr(self,sensor) + [data])

    def add_data(self, sensor, value):
        setattr(self, sensor, value)
        self.add_history(sensor, value)
        self._check_history()

    def _check_history(self):
        if self.ticker > self.history_check:
            for K in self.var_units.variables:
                if len(getattr(self, K + '_hist')) > self.limit_history:
                    setattr(self, K + '_hist', getattr(self, K + '_hist')[self.chunk:])
            self.ticker = 0
        else:
            self.ticker += 1
        
    def add_data(self, data):
        self.add_data(getattr(self.var_units, ))
    def add_temperature_data(self, data):
        self.add_data(self.var_units.temperature,data)
        
    def add_pressure_data(self, data):
        self.add_data(self.var_units.pressure,data)
    
    def add_humidity_data(self, data):
        self.add_data(self.var_units.humidity,data)

    def add_light_data(self, data):
        self.add_data(self.var_units.light,data)

    def add_oxidised_data(self, data):
        self.add_data(self.var_units.oxidising,data)

    def add_reduced_data(self, data):
        self.add_data(self.var_units.reducing,data)

    def add_nh3_data(self, data):
        self.add_data(self.var_units.nh3,data)
    
    def add_pm1_data(self, data):
        self.add_data(self.var_units.pm1,data)

    def add_pm25_data(self, data):
        self.add_data(self.var_units.pm25,data)

    def add_pm10_data(self, data):
        self.add_data(self.var_units.pm10,data)

    def add_noise_data(self, data):
        self.add_data(self.var_units.noise, data)
    


