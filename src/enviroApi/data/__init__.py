from enviroApi.config import Variable_Units
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Values(frozen=True):
    """Dataclass to hold values of sensor readings
    init:
        value (float): value of sensor reading
        timestamp (datetime): timestamp of when the value of read
        unit (str): Unit for the balues
    Returns:
        None
    """

    value: float
    timestamp: datetime
    unit: str
    name: str


class SensorData:
    """Class to hold data from sensors as well as historical data"""

    def __init__(
        limit_history: int = 604800,
        history_check: int = 10000,
        chunk: int = 86400,
        var_untits: Variable_Units = Variable_Units(),
    ):
        self.var_units = var_untits
        self.history_check = history_check
        self.limit_history = limit_history
        self.chunk = chunk
        self.data = {}
        self.data_log = {}

    def set_attributes(self):
        for K in self.var_units.variables:
            # setattr(self, K, 0)
            # setattr(self, K + '_hist', [])
            self.data[K] = Values(0.00, self.ts(), "XX", "No data available")
            self.history[K] = []

    def ts(self):
        return datetime.now()

    def add_data(self, sensor, value, timestamp: datetime = self.ts()):
        # setattr(self, sensor, value)
        self.data[sensor] = Values(
            value, timestamp, self.var_units.Dict[sensor], sensor
        )
        self.history[sensor] = self.history.get(sensor, []) + [self.data[sensor]]
        self._check_history(sensor)

    def _check_history(self, sensor: str):
        if len(self.history[sensor]) > self.history_check:
            self.history[sensor] = self.history[sensor][self.chunk :]

    # def add_data(self, data):
    #    self.add_data(getattr(self.var_units, ))

    def add_temperature_data(self, data) -> None:
        self.add_data(self.var_units.temperature, data)

    def add_pressure_data(self, data) -> None:
        self.add_data(self.var_units.pressure, data)

    def add_humidity_data(self, data) -> None:
        self.add_data(self.var_units.humidity, data)

    def add_light_data(self, data):
        self.add_data(self.var_units.light, data)

    def add_oxidised_data(self, data):
        self.add_data(self.var_units.oxidising, data)

    def add_reduced_data(self, data):
        self.add_data(self.var_units.reducing, data)

    def add_nh3_data(self, data):
        self.add_data(self.var_units.nh3, data)

    def add_pm1_data(self, data):
        self.add_data(self.var_units.pm1, data)

    def add_pm25_data(self, data):
        self.add_data(self.var_units.pm25, data)

    def add_pm10_data(self, data):
        self.add_data(self.var_units.pm10, data)

    def add_noise_data(self, data):
        self.add_data(self.var_units.noise, data)

    def get_data(self, sensor: str):
        return self.data.get(sensor, Values(0.00, self.ts(), "XX", "No data available"))

    def get_logs(
        self,
        sensor: str,
        history_length: int = 5,
        start_index: int = None,
        end_index: int = None,
    ) -> list:
        """_summary_

        Args:
            sensor (str): sensor
            history_length (int, optional): amount of data to return. Defaults to 5.
            start_index (int, optional): index to start history at. Defaults to 0.
            end_index (int, optional): index to end history at. Defaults to -1.

        Details:
            returns a given amount of history.
                If start_index and end_index are populated, then it will return data between the
                those index (inclusive), if the index are greater then the list, it will return
                as much data as possible. if end_index = -1, then it will return all the way to the end of the list
                If start_index or end_index is not populated, then it will return N, N-1, N-2....N-history_length - 1 of data.

        Return
            List
        """
        if start_index and end_index:
            if start_index > end_index:
                start_index, end_index = end_index, start_index
            data_len = len(self.history[sensor])
            if data_len > end_index - start_index:
                return self.history[sensor]
            elif end_index > data_len:
                return self.history[sensor][start_index:]
            else:
                return self.history.get(sensor)[start_index:end_index]

        return self.history[sensor][-1 * history_length :]
