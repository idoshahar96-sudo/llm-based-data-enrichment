
import pandas as pd

# evaluate the two models by KPIs
def coverage_rate(series):
    return (series != "Unknown").mean()
def usable_confidence_rate(conf_series):
    return conf_series.isin({"medium", "high"}).mean()
def agreement_rate(a, b):
    return (a == b).mean()

