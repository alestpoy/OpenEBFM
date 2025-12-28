"""
Unit tests for the Mean Trophic Level (MTL) calculation.
"""
import pytest
import pandas as pd
import logging
from src.metrics import calculate_mtl, TROPHIC_LEVELS


def test_calculate_mtl_basic():
    """Test MTL calculation with known species."""
    catch_data = pd.DataFrame({
        "species_name": ["Atlantic cod", "Pacific sardine", "Bluefin tuna"],
        "catch_kg": [100.0, 200.0, 50.0]
    })
    # Compute expected weighted average:
    # cod: 3.5 * 100 = 350
    # sardine: 2.8 * 200 = 560
    # tuna: 4.2 * 50 = 210
    # total weight = 350 + 560 + 210 = 1120
    # total catch = 100 + 200 + 50 = 350
    # mtl = 1120 / 350 = 3.2
    expected_mtl = (3.5*100 + 2.8*200 + 4.2*50) / 350
    result = calculate_mtl(catch_data)
    assert result == pytest.approx(expected_mtl, rel=1e-6)
    # Ensure result is float
    assert isinstance(result, float)


def test_calculate_mtl_with_unknown_species():
    """Test that unknown species are skipped with a warning."""
    catch_data = pd.DataFrame({
        "species_name": ["Atlantic cod", "Unknown fish", "Shrimp"],
        "catch_kg": [100.0, 50.0, 30.0]
    })
    # Unknown fish not in dictionary, should be skipped.
    # Expected MTL based on cod (3.5*100) + shrimp (2.5*30) = 350 + 75 = 425
    # total catch = 100 + 30 = 130
    # mtl = 425 / 130 ≈ 3.269230769
    expected_mtl = (3.5*100 + 2.5*30) / 130
    with pytest.warns(UserWarning, match="Species not found in trophic level dictionary"):
        # The function logs a warning, but we need to capture it.
        # We'll use caplog fixture.
        pass
    # Since we cannot rely on caplog with simple test, we'll just compute and compare.
    # Actually we can capture logs using caplog, but we need to import caplog.
    # Let's do a simpler test: ensure function runs and returns correct value.
    # We'll temporarily set logging to capture warnings.
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = calculate_mtl(catch_data)
        # Ensure at least one warning about unknown species
        assert len(w) >= 1
        assert "Species not found" in str(w[0].message)
    assert result == pytest.approx(expected_mtl, rel=1e-6)


def test_calculate_mtl_zero_catch():
    """Test that zero or negative catch values are ignored."""
    catch_data = pd.DataFrame({
        "species_name": ["Atlantic cod", "Pacific sardine"],
        "catch_kg": [0.0, -10.0]
    })
    # Both catches are invalid, so total_catch = 0 -> ValueError
    with pytest.raises(ValueError, match="No valid catch data"):
        calculate_mtl(catch_data)


def test_calculate_mtl_missing_column():
    """Test that missing required columns raise ValueError."""
    catch_data = pd.DataFrame({
        "species": ["Atlantic cod"],
        "weight": [100.0]
    })
    with pytest.raises(ValueError, match="must contain columns"):
        calculate_mtl(catch_data)


def test_calculate_mtl_non_dataframe():
    """Test that non-DataFrame input raises TypeError."""
    with pytest.raises(TypeError, match="Input must be a pandas DataFrame"):
        calculate_mtl([("Atlantic cod", 100)])


def test_trophic_level_dictionary():
    """Ensure trophic level dictionary is accessible and has numeric values."""
    assert isinstance(TROPHIC_LEVELS, dict)
    assert len(TROPHIC_LEVELS) > 0
    for species, tl in TROPHIC_LEVELS.items():
        assert isinstance(species, str)
        assert isinstance(tl, (int, float))
        assert tl >= 1.0  # trophic level should be at least 1 (primary producers)
        assert tl <= 5.0  # reasonable upper bound for marine fish