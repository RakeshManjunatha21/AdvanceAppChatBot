from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

client = GoogleAdsClient.load_from_storage("google-ads.yaml")

def fetch_ads_data(query: str, customer_id="1246259880"):
    try:
        ga_service = client.get_service("GoogleAdsService")
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        results = []
        for batch in stream:
            for row in batch.results:
                flat = {}
                for k, v in row.__dict__.items():
                    flat[k] = str(v)
                results.append(flat)
        return pd.DataFrame(results)
    except GoogleAdsException as e:
        print("GAQL Error:", e)
        return pd.DataFrame()

def parse_and_build_gaql(parsed):
    metric_fields = ", ".join([f"metrics.{m}" for m in parsed["metrics"]])
    dimension_fields = ", ".join([f"{d}" for d in parsed["dimensions"]])
    return f"""
        SELECT {dimension_fields}, {metric_fields}
        FROM campaign
        WHERE segments.date DURING {parsed['date_range']}
        ORDER BY metrics.{parsed['metrics'][0]} DESC
        LIMIT 10
    """
