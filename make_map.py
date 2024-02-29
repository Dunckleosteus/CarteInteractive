# Handling imports
from geopy.geocoders import Nominatim
import folium
import pandas as pd
import numpy as np
import geopandas as gpd
import os


# importing data
print("Opening excel data.xlsx... ", end="")
path = os.path.join("data.xlsx")
dataset = pd.read_excel(path)
print("Noot")
print("Renaming columns... ", end ="")
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
print("Noot")
head1 = ["Identite", "Entreprise1", "Ville", "Entreprise2", "Ville2", "ZIP", "Missions"]
# creating a subset of dataset called df
df = dataset[head1].copy()

print("Adding and filling town, company and x, y fields ", end="")
## ADDING NEW COLUMNS
# Adding text columns for Towns and companies
df.loc[:, "Ville0"] = pd.Series(["NULL"] * len(df))
df.loc[:, "Entreprise0"] = pd.Series(["NULL"] * len(df))

df.loc[:, "X"] = pd.Series([0] * len(df))
df.loc[:, "Y"] = pd.Series([0] * len(df))
# not sure what this is for
df.loc[:, "Ville0"] = df["Ville"].fillna(df["Ville2"]).copy()
# df.loc["Ville0", :] = df["Ville"].fillna(df["Ville2"]).copy()
df.loc[:, "Entreprise0"] = df["Entreprise1"].fillna(df["Entreprise2"]).copy()


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
print("Noot noot")

print("Creating and saving map ", end="")
### Creating subset of df
colonnes_a_conserver2 = ["Identite", "Entreprise0", "Ville0", "X", "Y", "Missions"]
full_df = df[colonnes_a_conserver2]

# Creating geodataframe from full_df
gens = gpd.GeoDataFrame(
    full_df,
    geometry=gpd.points_from_xy(full_df["Y"], full_df["X"]),
    crs="EPSG:4326",
)
# Setting godataframe projection
gens = gens.to_crs(4326)

# Setting script at bottom of map
attribution = "Coeur sur vous les dodos"

# Adding point for people to map, setting map as m
m = gens.explore(
    location=[48.858053, 2.2944991],
    tiles="cartodb positron",
    zoom_start=6,
    width=1000,
    height=500,
    attr=attribution,
)

# Adding green marker for UniLaSalle
folium.Marker(
    location=[49.460715173019175, 2.0705808327370465],
    popup="Maison",
    icon=folium.Icon(color="green", icon="ok-sign"),
).add_to(m)

# saving map as html to be displayed in index.html on github pages
m.save("map.html")
print(100*' NOOT')
