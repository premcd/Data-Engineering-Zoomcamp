"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


# the books endpoint is public; allow the caller to specify bibkeys
# to query. a sensible default ensures the pipeline can be executed
@dlt.source
def open_library_rest_api_source(
    bibkeys: str = "ISBN:0451526538",
):
    """Define dlt resources from REST API endpoints.

    Args:
        bibkeys: a comma-separated list of identifiers that the Open Library
            `/api/books` endpoint understands (e.g. "ISBN:0451526538").
            Defaults to a sample ISBN so the pipeline is runnable.
    """
    # The Open Library API is publicly accessible without authentication
    # We'll allow the caller to provide `bibkeys` as a parameter; some
    # default value makes the pipeline runnable out of the box.
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://openlibrary.org/",
            # no auth required for the books endpoint
        },
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    "path": "api/books",
                    "method": "GET",
                    # the API requires at least a bibkeys query parameter
                    # we expose it through the source function argument
                    "params": {
                        "bibkeys": bibkeys,
                        # return full data in json format
                        "format": "json",
                        "jscmd": "data",
                    },
                    # response returns a dictionary keyed by the requested bibkeys;
                    # we just want the raw JSON root object
                    "data_selector": "$",
                },
            }
        ],
        # no global defaults needed for now
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="open_library_pipeline",
    destination="duckdb",
    # `refresh="drop_sources"` ensures the data and the state is cleaned
    # on each `pipeline.run()`; remove the argument once you have a
    # working pipeline.
    refresh="drop_sources",
    # show basic progress of resources extracted, normalized files and load-jobs on stdout
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(open_library_rest_api_source())
    print(load_info)  # noqa: T201
