"""
Mean Trophic Level (MTL) calculation for fishery catch data.
"""

import logging
import pandas as pd

# Pre-defined trophic levels for common marine species
# Values are approximate trophic levels from literature
TROPHIC_LEVELS = {
    "Atlantic cod": 3.5,
    "Pacific sardine": 2.8,
    "Bluefin tuna": 4.2,
    "Anchovy": 2.7,
    "Mackerel": 3.2,
    "Squid": 3.0,
    "Shrimp": 2.5,
    "Lobster": 2.9,
    "Salmon": 3.8,
    "Halibut": 3.6,
    "Haddock": 3.3,
    "Plaice": 3.1,
    "Herring": 2.9,
    "Swordfish": 4.4,
    "Mahi-mahi": 3.7,
}

logger = logging.getLogger(__name__)


def calculate_mtl(catch_df: pd.DataFrame) -> float:
    """
    Calculate the weighted Mean Trophic Level of a catch.

    Parameters
    ----------
    catch_df : pandas.DataFrame
        Must contain columns 'species_name' (str) and 'catch_kg' (numeric).
        Each row represents a species and its catch weight in kilograms.

    Returns
    -------
    float
        Weighted mean trophic level of the catch.

    Notes
    -----
    Species not found in the internal trophic level dictionary are skipped
    with a warning. At least one valid species must be present; otherwise
    ValueError is raised.
    """
    if not isinstance(catch_df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    required_cols = {"species_name", "catch_kg"}
    if not required_cols.issubset(catch_df.columns):
        raise ValueError(f"DataFrame must contain columns {required_cols}")

    # Ensure catch_kg is numeric
    catch_df = catch_df.copy()
    catch_df["catch_kg"] = pd.to_numeric(catch_df["catch_kg"], errors="coerce")

    total_catch = 0.0
    weighted_sum = 0.0
    missing_species = []

    for _, row in catch_df.iterrows():
        species = row["species_name"]
        catch = row["catch_kg"]
        if pd.isna(catch) or catch <= 0:
            continue  # ignore invalid catch values

        if species in TROPHIC_LEVELS:
            tl = TROPHIC_LEVELS[species]
            weighted_sum += tl * catch
            total_catch += catch
        else:
            missing_species.append(species)

    if missing_species:
        logger.warning(
            f"Species not found in trophic level dictionary: {set(missing_species)}. "
            "These species are excluded from MTL calculation."
        )

    if total_catch == 0:
        raise ValueError(
            "No valid catch data with known trophic levels. Cannot compute MTL."
        )

    mtl = weighted_sum / total_catch
    return float(mtl)