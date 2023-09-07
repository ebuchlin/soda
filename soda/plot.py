from datetime import datetime, timedelta
import portion

from bokeh.io import output_file, show, save
from bokeh.models import MultiChoice, PanTool, BoxZoomTool, FixedTicker, Div
from bokeh.plotting import figure
from bokeh.layouts import gridplot, Spacer, column

from soda.availability import DataProduct
from soda.trajectory import get_traj


class DataAvailabilityPlotter:
    def __init__(self, output_filename='soda.html'):
        output_file(output_filename, title='SODA')
        datestr = datetime.now().strftime('%Y-%m-%d')
        tools = [PanTool(dimensions='width'),
                 BoxZoomTool(dimensions='width'),
                 'undo',
                 'redo',
                 'reset']
        self.plotter = figure(sizing_mode='stretch_width', plot_height=500,
                              x_axis_type='datetime', y_range=[],
                              x_range=(datetime(2020, 2, 10), datetime.now()),
                              tools=tools)
        self.plotter.ygrid.grid_line_color = None
        self.plotter.outline_line_color = None

        self.all_options = [
            # "EPD-EPT-ASUN-BURST-ELE-CLOSE", "EPD-EPT-ASUN-BURST-ION", "EPD-EPT-ASUN-HCAD", "EPD-EPT-ASUN-RATES", "EPD-EPT-NORTH-BURST-ELE-CLOSE", "EPD-EPT-NORTH-BURST-ION", "EPD-EPT-NORTH-HCAD", "EPD-EPT-NORTH-RATES", "EPD-EPT-SOUTH-BURST-ELE-CLOSE", "EPD-EPT-SOUTH-BURST-ION", "EPD-EPT-SOUTH-HCAD", "EPD-EPT-SOUTH-RATES", "EPD-EPT-SUN-BURST-ELE-CLOSE", "EPD-EPT-SUN-BURST-ION", "EPD-EPT-SUN-HCAD", "EPD-EPT-SUN-RATES", "EPD-HET-ASUN-BURST", "EPD-HET-ASUN-RATES", "EPD-HET-NORTH-BURST", "EPD-HET-NORTH-RATES", "EPD-HET-SOUTH-BURST", "EPD-HET-SOUTH-RATES", "EPD-HET-SUN-BURST", "EPD-HET-SUN-RATES", "EPD-SIS-A-HEHIST", "EPD-SIS-A-RATES-FAST", "EPD-SIS-A-RATES-MEDIUM", "EPD-SIS-A-RATES-SLOW", "EPD-SIS-B-HEHIST", "EPD-SIS-B-RATES-FAST", "EPD-SIS-B-RATES-MEDIUM", "EPD-SIS-B-RATES-SLOW", "EPD-STEP-BURST", "EPD-STEP-HCAD", "EPD-STEP-MAIN", "EPD-STEP-RATES",
            "EUI-FSI174-IMAGE", "EUI-FSI304-IMAGE", "EUI-HRIEUV174-IMAGE", "EUI-HRIEUVNON-IMAGE", "EUI-HRIEUVZER-IMAGE", "EUI-HRILYA1216-IMAGE",
            # "MAG-RTN-BURST", "MAG-RTN-LL", "MAG-RTN-LL-1-MINUTE", "MAG-RTN-NORMAL", "MAG-RTN-NORMAL-1-MINUTE", "MAG-SRF-BURST", "MAG-SRF-LL", "MAG-SRF-NORMAL", "MAG-VSO-BURST", "MAG-VSO-NORMAL", "MAG-VSO-NORMAL-1-MINUTE",
            "METIS-UV-IMAGE", "METIS-VL-IMAGE", "METIS-VL-PB", "METIS-VL-POL-ANGLE", "METIS-VL-STOKES", "METIS-VL-TB",
            "PHI-HRT-BAZI", "PHI-HRT-BINC", "PHI-HRT-BLOS", "PHI-HRT-BMAG", "PHI-HRT-ICNT", "PHI-HRT-STOKES", "PHI-HRT-VLOS",
            # "RPW-HFR-SURV", "RPW-LFR-SURV-ASM", "RPW-LFR-SURV-BP1", "RPW-LFR-SURV-BP2", "RPW-LFR-SURV-CWF-B", "RPW-LFR-SURV-CWF-E", "RPW-LFR-SURV-SWF-B", "RPW-LFR-SURV-SWF-E", "RPW-TDS-SURV-HIST1D", "RPW-TDS-SURV-HIST2D", "RPW-TDS-SURV-MAMP", "RPW-TDS-SURV-RSWF-B", "RPW-TDS-SURV-RSWF-E", "RPW-TDS-SURV-STAT", "RPW-TDS-SURV-TSWF-B", "RPW-TDS-SURV-TSWF-E", "RPW-TNR-SURV",
            "SOLOHI-1FT", "SOLOHI-1UT", "SOLOHI-1VT", "SOLOHI-2FT", "SOLOHI-2US", "SOLOHI-2UT", "SOLOHI-3FG", "SOLOHI-3FT", "SOLOHI-3UT", "SOLOHI-4FG", "SOLOHI-4UT",
            "SPICE-N-EXP", "SPICE-N-RAS", "SPICE-N-SIT", "SPICE-W-EXP", "SPICE-W-RAS", "SPICE-W-SIT",
            #"SWA-EAS-PAD-DEF", "SWA-EAS-PAD-DNF", "SWA-EAS-PAD-PSD", "SWA-EAS1-NM3D-DEF", "SWA-EAS1-NM3D-DNF", "SWA-EAS1-NM3D-PSD", "SWA-EAS1-SS-DEF", "SWA-EAS1-SS-DNF", "SWA-EAS1-SS-PSD", "SWA-EAS2-NM3D-DEF", "SWA-EAS2-NM3D-DNF", "SWA-EAS2-NM3D-PSD", "SWA-EAS2-SS-DEF", "SWA-EAS2-SS-DNF", "SWA-EAS2-SS-PSD", "SWA-PAS-EFLUX", "SWA-PAS-GRND-MOM", "SWA-PAS-VDF",
        ][::-1]

        '''
        self.multi_choice = MultiChoice(
            value=self.all_options,
            options=self.all_options,
            width_policy='fit',
            width=200,
            sizing_mode='stretch_height',
            title='Select data products')
        '''

        self.r_plot = figure(sizing_mode='stretch_width', plot_height=150,
                             x_axis_type='datetime', y_range=[0.25, 1.05],
                             x_range=self.plotter.x_range,
                             title='Radial distance',
                             tools=tools)
        self.phi_plot = figure(sizing_mode='stretch_width', plot_height=150,
                               x_axis_type='datetime', y_range=[0, 180],
                               x_range=self.plotter.x_range,
                               title='Earth-Orbiter angle',
                               tools=tools)
        self.phi_plot.yaxis[0].ticker = FixedTicker(ticks=[0, 90, 180])
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
        for desc in self.all_options:
            self.add_interval_data(desc)

        # self.multi_choice.js_link("value", self.plotter.y_range, "factors")
        self.plotter.y_range.factors = self.all_options

    def add_interval_data(self, descriptor):
        product = DataProduct(descriptor)
        intervals = self.merge_intervals(product.intervals)
        for interval in intervals:
            self.plotter.hbar(y=[descriptor],
                              left=interval.lower,
                              right=interval.upper,
                              height=0.5,
                              color=self.get_color(descriptor))

    def add_trajectory(self):
        dates, r, sun_earth_angle = get_traj()
        self.r_plot.line(x=dates, y=r)
        self.phi_plot.line(x=dates, y=sun_earth_angle)

    @staticmethod
    def get_color(descriptor):
        return {'EUI': '#e41a1c',
                'MAG': '#377eb8',
                'SWA': '#4daf4a',
                'RPW': '#984ea3',
                'EPD': '#ff7f00',
                'SPI': '#a65628',
                'SOL': '#dd1c77',
                'PHI': '#00cccc',
                'MET': '#aacc00'
                }[descriptor[:3]]

    @staticmethod
    def merge_intervals(intervals):
        intervals = intervals.sort_values(by='Start')
        start_dates = intervals['Start'].map(lambda t: t.date()).unique()
        end_dates = (intervals['End'] +
                     timedelta(days=1) -
                     timedelta(microseconds=1)).map(lambda t: t.date()).unique()
        intervals = portion.empty()
        for start, end in zip(start_dates, end_dates):
            intervals = intervals | portion.closed(start, end)
        return intervals

    def show(self):
        show(self.layout)

    def save(self):
        save(self.layout)
