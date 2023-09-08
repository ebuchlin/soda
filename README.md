This is a fork of [David Stansby's SODA](https://github.com/dstansby/soda).


Solar Orbiter Data Availability (SODA)
======================================

A tool to visualise the data availability of Solar Orbiter data products.
The dashboard for remote-sensing instruments data can be viewed at
https://spice.ias.u-psud.fr/spice-data/data-availability/.

Usage
-----

`python run_soda_noshow.py` will run SODA, and create an updated static `index.html` file that
can be uploaded to a server.
`python run_soda.py` does the same, and also displays the result in a browser.

Automatic deployment
--------------------
Github actions can be used automatically deploys a new HTML file to the `pages` branch
every time a commit is pushed to the main branch. They are not active on this repository at the moment.

Feedback/support
----------------
If you have any problems or suggestions for SODA, please open an issue at https://github.com/ebuchlin/soda/issues.
