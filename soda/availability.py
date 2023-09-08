from pathlib import Path
import pandas as pd

from soda.soar_query import SoarQuery


_MISSION_BEGIN = pd.Timestamp("2020-01-01")
_NOW = pd.Timestamp("now")
_CACHE_DIR = (Path(__file__) / '..' / '.data').resolve()
_CACHE_DIR.mkdir(exist_ok=True)


class DataProduct:
    def __init__(self, descriptor, low_latency=False):
        """
        Parameters
        ----------
        descriptor: str
            Data product descriptor. These can be found by searching for data
            on http://soar.esac.esa.int/soar/#search, and identifying the
            descriptor from the "Descriptor" column.
        low_latency: bool, optional
            If `True`, query low latency data instead of science data.
        """
        self.descriptor = descriptor
        self.low_latency = low_latency

    @property
    def latest_path(self):
        """
        Path to data updated today.
        """
        datestr = _NOW.strftime('%Y-%m-%d')
        return _CACHE_DIR / f'{self.descriptor}_{datestr}.csv'

    @property
    def intervals(self):
        """
        All available intervals for this data product.
        """
        if not self.latest_path.exists():
            self.save_remote_intervals()

        df = pd.read_csv(self.latest_path,
                         parse_dates=['Start', 'End'])
        return df

    def save_remote_intervals(self):
        """
        Get and save the intervals of all data files available in the
        Solar Orbiter Archive for a given data descriptor.
        """
        print(f'Updating intervals for {self.descriptor}...')
        begin_time = _MISSION_BEGIN.isoformat(sep=" ")
        end_time = _NOW.isoformat(sep=" ")
        soar = SoarQuery()
        result = soar.get_availability(
            self.descriptor,
            begin_time, end_time,
            low_latency=self.low_latency
        )

        # Do some list/dict wrangling
        names = [m['name'] for m in result['metadata']]
        info = {name: [] for name in names}
        for entry in result['data']:
            for i, name in enumerate(names):
                info[name].append(entry[i])

        # Setup intervals
        intervals = []
        for start, end in zip(info['begin_time'], info['end_time']):
            intervals.append([pd.Timestamp(start).to_pydatetime(),
                              pd.Timestamp(end).to_pydatetime()])

        df = pd.DataFrame(intervals, columns = ['Start', 'End'])
        df.to_csv(self.latest_path, index=False)
