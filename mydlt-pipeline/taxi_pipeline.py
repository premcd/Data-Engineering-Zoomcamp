"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


# the taxi dataset is public; no authentication required
@dlt.source
def taxi_pipeline_rest_api_source():
    """returns pages of taxi trip records from the NYC API.

    Pagination is controlled via a `page` query parameter; the service
    returns an empty array when there are no more pages.  We configure
    a `page_number` paginator to increment until an empty page is seen.
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
            # no auth
        },
        # default parameters sent with each request; the paginator will
        # override `page` as it iterates.
        "resource_defaults": {"endpoint": {"params": {"page": 1}}},
        "resources": [
            {
                "name": "trips",
                "endpoint": {
                    # root path returns the array
                    "path": "",
                    "method": "GET",
                    "data_selector": "$",  # response is plain array
                    "paginator": {
                        "type": "page_number",
                        "base_page": 1,
                        # the API returns plain arrays and doesn't include
                        # a `total` key.  `PageNumberPaginator` normally
                        # looks for that key unless we explicitly disable
                        # it.  setting `total_path` to None tells the
                        # paginator to rely solely on
                        # `stop_after_empty_page` (or a max page) instead.
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                },
            }
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    # `refresh="drop_sources"` ensures the data and the state is cleaned
    # on each `pipeline.run()`; remove the argument once you have a
    # working pipeline.
    refresh="drop_sources",
    # show basic progress of resources extracted, normalized files and load-jobs on stdout
    # the previous run printed every page payload which flooded the
    # terminal; omit `progress` or set to a valid collector when ready.
    # progress="none",  # not a valid value
)


if __name__ == "__main__":
    load_info = pipeline.run(taxi_pipeline_rest_api_source())
# print(load_info)  # noqa: T201
