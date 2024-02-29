# Handling imports
from geopy.geocoders import Nominatim
import folium
import pandas as pd
import numpy as np
import geopandas as gpd
import os


# importing data
path = os.path.join("data.xlsx")
dataset = pd.read_excel(path)
ancien_nom_vers_nouveau_nom = {
    "Nom": "Identite",
    "Dans quelle entreprise es-tu en stage ?": "Entreprise1",
    "Dans quelle ville a lieu ton stage ?": "Ville",
    "Quelle est ton entreprise ?": "Entreprise2",
    "Dans quelle ville es-tu en alternance ?": "Ville2",
    "Code postal de ton lieu de stage": "ZIP",
    "Raconte nous ce que tu fais ou tes missions dans ce petit paragraphe suivant (pas obligatoire)": "Missions"
    # ...
}

dataset = dataset.rename(columns=ancien_nom_vers_nouveau_nom)
# dataset2 = dataset.rename(columns=ancien_nom_vers_nouveau_nom)
head1 = ["Identite", "Entreprise1", "Ville", "Entreprise2", "Ville2", "ZIP", "Missions"]

# not sure why we are making a subset
# df = dataset2[head1]
df = dataset[head1]


## ADDING NEW COLUMNS
# Adding text columns for Towns and companies
df["Ville0"] = pd.Series(["NULL"] * len(df))
df["Entreprise0"] = pd.Series(["NULL"] * len(df))

df["X"] = pd.Series([0] * len(df))
df["Y"] = pd.Series([0] * len(df))
# not sure what this is for
df["Ville0"] = df["Ville"].fillna(df["Ville2"])
df["Entreprise0"] = df["Entreprise1"].fillna(df["Entreprise2"])

# saving to csv (not sure why)
# df.to_csv("CSV.csv")


# Import des coordonnées X et Y
def g(df):
    # Vérifie si la valeur est un entier
    is_numeric = df["ZIP"].str.isdigit()
    # Vérifie si la valeur a 5 caractères
    is_correct_length = df["ZIP"].str.len() == 5
    # Filtre le dataframe en conservant uniquement les lignes valides
    df = df[is_numeric & is_correct_length]
    return df


df = g(df.copy())

### GETTING x, y LOCATION FROM ZIP CODES
locator = Nominatim(user_agent="my_app")
df["Adresse"] = df["ZIP"].apply(lambda x: str(x) + ", France")

df["X"] = df["Adresse"].apply(lambda x: locator.geocode(x).latitude)
df["Y"] = df["Adresse"].apply(lambda x: locator.geocode(x).longitude)


### Creating subset of df
colonnes_a_conserver2 = ["Identite", "Entreprise0", "Ville0", "X", "Y", "Missions"]
full_df = df[colonnes_a_conserver2]
full_df.to_csv("Clean.csv")

datasetmap = pd.read_csv(os.path.join("Clean.csv"))

gens = gpd.GeoDataFrame(
    datasetmap,
    geometry=gpd.points_from_xy(datasetmap["Y"], datasetmap["X"]),
    crs="EPSG:4326",
).to_file("gens_point.shp")


gens_point = gpd.read_file(os.path.join("gens_point.shp"))
gens_point = gens_point.to_crs(4326)

attribution = "Coeur sur vous les dodos"

m = gens_point.explore(
    location=[48.858053, 2.2944991],
    tiles="cartodb positron",
    zoom_start=6,
    width=1000,
    height=500,
    attr=attribution,
)


folium.Marker(
    location=[49.460715173019175, 2.0705808327370465],
    popup="Maison",
    icon=folium.Icon(color="green", icon="ok-sign"),
).add_to(m)


m.save("map.html")
