import os
from arcgis.gis import GIS
from dotenv import load_dotenv
from typing import Optional, Tuple
from arcgis.features import GeoAccessor, FeatureLayer, Feature
from arcgis.geometry import Point
# ---------------------------------------------------------------------------- #
#  Helper: authenticate via Pro, Home, or .env credentials                     #
# ---------------------------------------------------------------------------- #
def get_gis(portal_url: Optional[str],
            user: Optional[str],
            pwd:  Optional[str]) -> GIS:
    for profile in ("pro", "home"):
        try:
            print(f"Trying GIS('{profile}') …")
            return GIS(profile)
        except Exception as e:
            print(f"    {profile!r} login failed: {e}")
    if portal_url and user and pwd:
        print(f"Trying .env creds for {portal_url} …")
        return GIS(portal_url, user, pwd)
    raise RuntimeError("All GIS authentication methods failed.")


# ---------------------------------------------------------------------------- #
#  Helper: build a rounded-XY key for a point                                   #
# ---------------------------------------------------------------------------- #
def geom_key(x: float, y: float, decimals: int) -> Tuple[float, float]:
    """
    Round X and Y to the given number of decimal places.
    Returns a tuple that can be used as a set key.
    """
    return (round(x, decimals), round(y, decimals))

# ---------------------------------------------------------------------------- #
#  Main workflow                                                                #
# ---------------------------------------------------------------------------- #
def upload_points(news_df, args):
    # ------------------------------------------------------------------------ #
    # 1) Load configuration from .env                                          #
    # ------------------------------------------------------------------------ #
    load_dotenv()  # looks for .env in CWD or parents

    portal_url = os.getenv("AGOL_URL")
    username   = os.getenv("AGOL_USERNAME")
    password   = os.getenv("AGOL_PASSWORD")

    item_id    = os.getenv("FEATURE_SERVICE_ITEMID")
   # local_fc   = os.getenv("LOCAL_FEATURE_CLASS")
    xy_decimals = int(os.getenv("XY_DECIMALS", "6"))

    # Validate required settings
    if not all([item_id]):
        raise ValueError(
            "Please set the FEATURE_SERVICE_ITEMID in .env."
        )

    # ------------------------------------------------------------------------ #
    # 2) Authenticate & get the hosted layer                                   #
    # ------------------------------------------------------------------------ #
    gis = get_gis(portal_url, username, password)
    print("Authenticated.")

    layer: FeatureLayer = gis.content.get(item_id).layers[0]
    print(f"Connected to hosted layer: {layer.properties.name}\n")

    # ------------------------------------------------------------------------ #
    # 3) Fetch existing geometry keys from AGOL                                #
    # ------------------------------------------------------------------------ #
    print(f"Fetching existing feature coordinates (rounded to {xy_decimals} dp)…")
    fs_existing = layer.query(where="1=1",
                              out_fields="*",
                              return_geometry=True)
    existing_keys = {
        geom_key(feat.geometry["x"], feat.geometry["y"], xy_decimals)
        for feat in fs_existing
    }
    print(f"  {len(existing_keys):,} existing features on service.\n")

    # ------------------------------------------------------------------------ #
    # 4) Load local FC and build local FeatureSet                              #
    # ------------------------------------------------------------------------ #


    news_df = news_df[news_df['Lat'].notna() & (news_df['Lat'] != '') & news_df['Long'].notna() & (news_df['Long'] != '')]
    #
    # ------------------------------------------------------------------------ #
    # 5) Filter to only those whose geometry key is not already online         #
    # ------------------------------------------------------------------------ #
    to_add = []
    for index,row in news_df.iterrows():

        key = geom_key(row["Long"], row["Lat"], xy_decimals)
        if key not in existing_keys:
            # Define the point geometry
            # Create a Feature object
            new_feature =  {
                "geometry": {"x": float(row['Long']), "y": float(row['Lat']), "spatialReference": {"wkid": 4326}},
                "attributes": {},
            }
            print(new_feature)
            to_add.append(new_feature)

    if not to_add:
        print("🎉  No new features to add – all geometries already present.")
        return

    print(f"  {len(to_add):,} new feature(s) to upload.\n")

    # # ------------------------------------------------------------------------ #
    # 6) Upload new features                                                   #
    # ------------------------------------------------------------------------ #
    print("Uploading …")

    result = layer.edit_features(adds=to_add)
    added = sum(1 for r in result.get("addResults", []) if r.get("success"))
    print(f"{added} feature(s) added.  Check AGOL to confirm.")
# ---------------------------------------------------------------------------- #
