from datetime import datetime, timedelta
import portion
import pandas as pd

from bokeh.io import output_file, show, save
from bokeh.models import PanTool, BoxZoomTool, FixedTicker, Div
from bokeh.plotting import figure
from bokeh.layouts import gridplot, column

from soda.availability import DataProduct
from soda.trajectory import get_traj
from soda.soar_query import SoarQuery


class DataAvailabilityPlotter:
    def __init__(self, output_filename='soda.html'):
        output_file(output_filename, title='SODA')
        datestr = datetime.now().strftime('%Y-%m-%d')
        tools = [PanTool(dimensions='width'),
                 BoxZoomTool(dimensions='width'),
                 'undo',
                 'redo',
                 'reset']
        self.plotter = figure(sizing_mode='stretch_width', plot_height=600,
                              x_axis_type='datetime', y_range=[],
                              x_range=(datetime(2020, 2, 10), datetime.now()),
                              tools=tools)
        self.plotter.ygrid.grid_line_color = None
        self.plotter.outline_line_color = None

        instruments = ["EUI", "METIS", "PHI", "SOLOHI", "SPICE", "STIX"]
        soar = SoarQuery()
        self.all_options = soar.get_descriptors(instruments)[::-1]

        self.r_plot = figure(sizing_mode='stretch_width', plot_height=100,
                             x_axis_type='datetime', y_range=[0.25, 1.05],
                             x_range=self.plotter.x_range,
                             title='Radial distance',
                             tools=tools)
        self.phi_plot = figure(sizing_mode='stretch_width', plot_height=100,
                               x_axis_type='datetime', y_range=[0, 180],
                               x_range=self.plotter.x_range,
                               title='Earth-Orbiter angle',
                               tools=tools)
        self.phi_plot.yaxis[0].ticker = FixedTicker(ticks=[0, 90, 180])
        self.r_plot.yaxis[0].ticker = FixedTicker(ticks=[0.25, 0.5, 0.75, 1])
        self.add_trajectory()

        url = '<a href="http://soar.esac.esa.int/soar/">Solar Orbiter Archive</a>'
        self.title = Div(
            text=(f"<h1>Solar Orbiter data availability</h1> "
                  f"Last updated {datestr}, daily resolution, "
                  f"all data available at the {url}"))
        self.title.style = {'text-align': 'center'}

        panels = [self.plotter, self.r_plot, self.phi_plot]
        for p in panels + [self.title]:
            p.align = 'center'
        layout = gridplot(panels, ncols=1,
                          sizing_mode='stretch_width',
                          toolbar_location='right')
        self.layout = column([self.title, layout], sizing_mode='stretch_width')
        # top, right, bottom, left
        self.layout.margin = (0, 75, 0, 75)
        # Add data
        factors = []
        for desc in self.all_options:
            is_added = self.add_interval_data(desc)
            if is_added:
                factors.append(desc)
        self.plotter.y_range.factors = factors

    def add_interval_data(self, descriptor):
        product = DataProduct(descriptor)
        # do not plot products with less than 1% total observation duration in 2022
        duration = product.total_duration(pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01"))
        reference_duration = pd.Timedelta(days=365)
        if duration.total_seconds() / reference_duration.total_seconds() < 0.005:
            return False
        intervals = self.merge_intervals(product.intervals)
        for interval in intervals:
            self.plotter.hbar(y=[descriptor],
                              left=interval.lower,
                              right=interval.upper,
                              height=0.5,
                              color=self.get_color(descriptor))
        return True

    def add_trajectory(self):
        dates, r, sun_earth_angle = get_traj()
        self.r_plot.line(x=dates, y=r)
        self.phi_plot.line(x=dates, y=sun_earth_angle)

    @staticmethod
    def get_color(descriptor):
        instrument = descriptor[:3].upper()
        return {'EUI': '#e41a1c',
                'MAG': '#377eb8',
                'SWA': '#4daf4a',
                'RPW': '#984ea3',
                'EPD': '#ff7f00',
                'SPI': '#a65628',
                'SOL': '#dd1c77',
                'PHI': '#00cccc',
                'MET': '#aacc00',
                'STI': '#444444'
                }[instrument]

    @staticmethod
    def merge_intervals(intervals):
        intervals = intervals.sort_values(by='Start')
        start_dates = intervals['Start'].map(lambda t: t.date()).unique()
        end_dates = (
            intervals['End'] +
            (timedelta(days=1) - timedelta(microseconds=1))
        ).map(lambda t: t.date()).unique()
        intervals = portion.empty()
        for start, end in zip(start_dates, end_dates):
            intervals = intervals | portion.closed(start, end)
        return intervals

    def show(self):
        show(self.layout)

    def save(self):
        save(self.layout)
