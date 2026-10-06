import pandas as pd
from rag import search_places

trains = pd.read_csv("data/trains.csv")

def search_trains(from_city: str, to_city: str):
    """Find trains between two cities."""
    m = trains[
        trains["from_city"].str.lower().eq(from_city.lower())
        & trains["to_city"].str.lower().eq(to_city.lower())
    ]
    if m.empty:
        return "No trains found in dataset."
    return m.to_dict(orient="records")

def find_places(query: str, city: str = ""):
    """Find tourist places in a city that match what the traveller wants."""
    return search_places(query, city)