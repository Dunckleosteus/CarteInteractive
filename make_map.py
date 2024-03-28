# Handling imports
from geopy.geocoders import Nominatim
import folium
import pandas as pd
import geopandas as gpd
import os


def open_excel_file(path: str):
    return pd.read_excel(path)


def rename_columns(df):
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
    return df.rename(columns=ancien_nom_vers_nouveau_nom)


def g(df):
    # Vérifie si la valeur est un entier
    is_numeric = df["ZIP"].str.isdigit()
    # Vérifie si la valeur a 5 caractères
    is_correct_length = df["ZIP"].str.len() == 5
    # Filtre le dataframe en conservant uniquement les lignes valides
    df = df[is_numeric & is_correct_length]
    return df


def geocode_towns(df):
    locator = Nominatim(user_agent="my_app")
    df["Adresse"] = df["ZIP"].apply(lambda x: str(x) + ", France")

    df["X"] = df["Adresse"].apply(lambda x: locator.geocode(x).latitude)
    df["Y"] = df["Adresse"].apply(lambda x: locator.geocode(x).longitude)
    return df


def create_geodataframe_from_dataframe(df):
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Y"], df["X"]),
        crs="EPSG:4326",
    )
    # Setting godataframe projection
    gdf = gdf.to_crs(4326)
    return gdf


# set this variable to true if you have a new version of the input excel
# and you want to geocode everything all over again.
update_positions = False


def main():
    if update_positions:
        df = open_excel_file(os.path.join("data2.xlsx"))
        df = rename_columns(df)
        df = df[["Identite", "Entreprise1", "Ville",
                 "Entreprise2", "Ville2", "ZIP", "Missions"]]

        # creating Town column
        df["Ville0"] = None
        df["Entreprise0"] = None

        df["X"] = 0
        df["Y"] = 0

        # not sure what this is for
        df.loc[:, "Ville0"] = df["Ville"].fillna(df["Ville2"]).copy()
        # df.loc["Ville0", :] = df["Ville"].fillna(df["Ville2"]).copy()
        df.loc[:, "Entreprise0"] = df["Entreprise1"].fillna(
            df["Entreprise2"]).copy()

        df = g(df)
        df = geocode_towns(df)
        # not sure why we are creating another subset
        df = df[["Identite", "Entreprise0", "Ville0", "X", "Y", "Missions"]]

        # saving file so as to not have to do the steps above every time
        # manual modifications can thus be done on cache directly
        df.to_excel("cache.xlsx")

    df = open_excel_file("cache.xlsx")
    gens = create_geodataframe_from_dataframe(df)

    # Creating geodataframe from full_df

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


if __name__ == "__main__":
    main()
