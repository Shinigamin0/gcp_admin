from google.oauth2 import service_account
from google.cloud import compute_v1
from collections import defaultdict
from collections.abc import Iterable
from google.cloud import monitoring_v3
from pprint import pprint as pp
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class computeEngineManager:

    def __init__(self, projectId: str, json_route: str):
        self.credentials = service_account.Credentials.from_service_account_file(json_route)
        self.compute_engine_client = compute_v1.InstancesClient(credentials=self.credentials)
        self.monitoring_client = monitoring_v3.MetricServiceClient(credentials=self.credentials)
        self.project_id = projectId
       

    def list_all_instances(self) -> dict[str, Iterable[compute_v1.Instance]]:
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = self.project_id
        request.max_results = 50

        agg_list = self.compute_engine_client.aggregated_list(request=request)

        all_instances = defaultdict(list)

        for zone, response in agg_list:
            if response.instances:
                all_instances[zone].extend(response.instances)
        return all_instances


    def get_cpu_use(self, start: datetime, end: datetime, period: str, instanceId: str, aligner: str ):

        project_name = "projects/" + self.project_id

        start_datetime = datetime.datetime.strptime(start, '%d/%m/%y')
        end_datetime = datetime.datetime.strptime(end, '%d/%m/%y')

        start_time_seconds = int(datetime.datetime.timestamp(start_datetime))
        end_time_seconds = int(datetime.datetime.timestamp(end_datetime))
        
        if period == 'minutes':
            alignment_period = 60
        elif period == 'hours':
            alignment_period = 3600
        elif period == 'days':
            alignment_period = 86400
        elif period == 'weeks':
            alignment_period = 604800
        else:
            alignment_period = 3600

        if aligner == 'max':
            per_series_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_MAX

        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {"seconds": end_time_seconds, "nanos": 0},
                "start_time": {"seconds": start_time_seconds, "nanos": 0},
            }
        )

        aggregation = monitoring_v3.Aggregation(
            {
                "alignment_period": {"seconds": alignment_period},
                "per_series_aligner": per_series_aligner,
            }
        )

        request={
            "name": project_name,
            "filter": 'metric.type = "compute.googleapis.com/instance/cpu/utilization"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": aggregation,
        }

        results = self.monitoring_client.list_time_series(request)

        metrics = {}
        for result in results:
            for i  in range(len(result.points)):
                key = str(result.points[i].interval.start_time).split('+')[0]
                value = str(result.points[i].value.double_value)
                metrics[key]=value
        
        return metrics