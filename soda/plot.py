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
            # "epd-ept-asun-burst-ele-close", "epd-ept-asun-burst-ion", "epd-ept-asun-hcad", "epd-ept-asun-rates", "epd-ept-north-burst-ele-close", "epd-ept-north-burst-ion", "epd-ept-north-hcad", "epd-ept-north-rates", "epd-ept-south-burst-ele-close", "epd-ept-south-burst-ion", "epd-ept-south-hcad", "epd-ept-south-rates", "epd-ept-sun-burst-ele-close", "epd-ept-sun-burst-ion", "epd-ept-sun-hcad", "epd-ept-sun-rates", "epd-het-asun-burst", "epd-het-asun-rates", "epd-het-north-burst", "epd-het-north-rates", "epd-het-south-burst", "epd-het-south-rates", "epd-het-sun-burst", "epd-het-sun-rates", "epd-sis-a-hehist", "epd-sis-a-rates-fast", "epd-sis-a-rates-medium", "epd-sis-a-rates-slow", "epd-sis-b-hehist", "epd-sis-b-rates-fast", "epd-sis-b-rates-medium", "epd-sis-b-rates-slow", "epd-step-burst", "epd-step-hcad", "epd-step-main", "epd-step-rates",
            "eui-fsi174-image", "eui-fsi304-image", "eui-hrieuv174-image", "eui-hrieuvnon-image", "eui-hrieuvzer-image", "eui-hrilya1216-image",
            # "mag-rtn-burst", "mag-rtn-ll", "mag-rtn-ll-1-minute", "mag-rtn-normal", "mag-rtn-normal-1-minute", "mag-srf-burst", "mag-srf-ll", "mag-srf-normal", "mag-vso-burst", "mag-vso-normal", "mag-vso-normal-1-minute",
            "metis-uv-image", "metis-vl-image", "metis-vl-pb", "metis-vl-pol-angle", "metis-vl-stokes", "metis-vl-tb",
            "phi-hrt-bazi", "phi-hrt-binc", "phi-hrt-blos", "phi-hrt-bmag", "phi-hrt-icnt", "phi-hrt-stokes", "phi-hrt-vlos",
            # "rpw-hfr-surv", "rpw-lfr-surv-asm", "rpw-lfr-surv-bp1", "rpw-lfr-surv-bp2", "rpw-lfr-surv-cwf-b", "rpw-lfr-surv-cwf-e", "rpw-lfr-surv-swf-b", "rpw-lfr-surv-swf-e", "rpw-tds-surv-hist1d", "rpw-tds-surv-hist2d", "rpw-tds-surv-mamp", "rpw-tds-surv-rswf-b", "rpw-tds-surv-rswf-e", "rpw-tds-surv-stat", "rpw-tds-surv-tswf-b", "rpw-tds-surv-tswf-e", "rpw-tnr-surv",
            "solohi-1ft", "solohi-1ut", "solohi-1vt", "solohi-2ft", "solohi-2us", "solohi-2ut", "solohi-3fg", "solohi-3ft", "solohi-3ut", "solohi-4fg", "solohi-4ut",
            "spice-n-exp", "spice-n-ras", "spice-n-sit", "spice-w-exp", "spice-w-ras", "spice-w-sit",
            #"swa-eas-pad-def", "swa-eas-pad-dnf", "swa-eas-pad-psd", "swa-eas1-nm3d-def", "swa-eas1-nm3d-dnf", "swa-eas1-nm3d-psd", "swa-eas1-ss-def", "swa-eas1-ss-dnf", "swa-eas1-ss-psd", "swa-eas2-nm3d-def", "swa-eas2-nm3d-dnf", "swa-eas2-nm3d-psd", "swa-eas2-ss-def", "swa-eas2-ss-dnf", "swa-eas2-ss-psd", "swa-pas-eflux", "swa-pas-grnd-mom", "swa-pas-vdf",
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
        instrument = descriptor[:3].upper()
        return {'EUI': '#e41a1c',
                'MAG': '#377eb8',
                'SWA': '#4daf4a',
                'RPW': '#984ea3',
                'EPD': '#ff7f00',
                'SPI': '#a65628',
                'SOL': '#dd1c77',
                'PHI': '#00cccc',
                'MET': '#aacc00'
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
