import requests


class SoarQuery:
    tap_end_point = 'http://soar.esac.esa.int/soar-sl-tap/tap/'

    def __init__(self):
        pass

    def _soar_sync_query(self, adql_query):
        """
        SOAR synchronous TAP query

        Parameters
        ----------
        adql_query: str
            ADQL query

        Return
        ------
        dict
            JSON query result
        """
        payload = {
            'REQUEST': 'doQuery',
            'LANG': 'ADQL',
            'FORMAT': 'json',
            'QUERY': adql_query
        }
        r = requests.get(f'{self.tap_end_point}sync', params=payload)
        return r.json()

    def get_descriptors(self, instruments):
        """
        Get a list of file descriptors for the given instruments

        Parameters
        ----------
        instruments: list[str]
            List of instruments
        """
        query = "SELECT DISTINCT descriptor FROM soar.v_sc_data_item"
        result = self._soar_sync_query(query)
        descriptors = [descriptor[0] for descriptor in result["data"]]
        return sorted(
            filter(
                lambda d: d.split("-")[0].upper() in instruments,
                descriptors
            )
        )

    def get_availability(self, descriptor, begin_time, end_time, low_latency=False):
        """
        Get data availability from SOAR for the given descriptor and time range

        Parameters
        ----------
        descriptor: str
            Data product descriptor
        begin_time: pandas.Timestamp
            Start of time range
        end_time: pandas.Timestamp
            End of time range
        low_latency: bool
            If True, select low latency data
        """
        query = {}
        query['SELECT'] = '*'
        if low_latency:
            query['FROM'] = 'v_ll_data_item'
        else:
            query['FROM'] = 'v_sc_data_item'
        query['WHERE'] = (f"descriptor='{descriptor}' AND "
                          f"begin_time<='{end_time}' AND "
                          f"begin_time>='{begin_time}'")
        adql = ' '.join([f'{item} {query[item]}' for
                                          item in query])
        result = self._soar_sync_query(adql)
        return result
