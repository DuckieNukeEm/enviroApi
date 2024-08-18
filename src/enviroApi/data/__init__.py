


class SensorData():

    def __init__(limit_history = 604800, history_check = 10000, history_remove_amt = 86400 ):
        self.var_units = {"temp":"C",
             "press":"hPa",
             "humidity": "%",
             "light": "Lux",
             "oxi": "kO",
             "redu": "kO",
             "nh3": "kO",
             "pm1": "ug/m3",
             "pm25": "ug/m3",
             "pm10": "ug/m3"}
        self.ticker = 0
        self.history_check = history_check
        self.limit_history = limit_history
        self.chunk = history_remove_amt

    def set_attributes(self):
        for K in self.var_units.keys():
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
            for K in self.var_units.keys():
                if len(getattr(self, K + '_hist')) > self.limit_history:
                    setattr(self, K + '_hist', getattr(self, K + '_hist')[self.chunk:])
            self.ticker = 0
        else:
            self.ticker += 1
        
    def add_temperature_data(self, data):
        self.add_data('temp',data)
        
    def add_pressure_data(self, data):
        self.add_data('press',data)
    
    def add_humidity_data(self, data):
        self.add_data('humidity',data)

    def add_light_data(self, data):
        self.add_data('light',data)

    def add_oxidised_data(self, data):
        self.add_data('oxi',data)

    def add_reduced_data(self, data):
        self.add_data('press',data)

    def add_nh3_data(self, data):
        self.add_data('nh3',data)
    
    def add_pm1_data(self, data):
        self.add_data('pm1',data)

    def add_pm25_data(self, data):
        self.add_data('pm25',data)

    def add_pm10_data(self, data):
        self.add_data('pm10',data)
    



variables = {"temp":"C",
             "press":"hPa",
             "humidity": "%",
             "light": "Lux",
             "oxi": "kO",
             "redu": "kO",
             "nh3": "kO",
             "pm1": "ug/m3",
             "pm25": "ug/m3",
             "pm10": "ug/m3"}


                own_disp_values["P2.5"] = own_disp_values["P2.5"][1:] + [[own_data["P2.5"][1], 1]]
            own_data["P10"][1] = pm_values.pm_ug_per_m3(10)
            own_disp_values["P10"] = own_disp_values["P10"][1:] + [[own_data["P10"][1], 1]]
            own_data["P1"][1] = pm_values.pm_ug_per_m3(1.0)
            own_disp_values["P1"] = own_disp_values["P1"][1:] + [[own_data["P1"][1], 1]]