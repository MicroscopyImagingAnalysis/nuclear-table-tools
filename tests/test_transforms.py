import pandas as pd

from nuclear_table_tools import (
    AdvancedOperator,
    drop_high_corr_columns,
    drop_high_corr_columns_marker,
    merge_with_VAE_df,
)


def test_merge_with_vae_preserves_join_contract():
    features = pd.DataFrame(
        {
            "condition": ["Day1"],
            "batch": ["B1"],
            "subbatch": ["S1"],
            "label-id": [7],
            "file": ["/images/sample.nd2"],
        }
    )
    vae = pd.DataFrame(
        {
            "id": [1],
            "label": ["Day1"],
            "batch_label": ["B1"],
            "subbatch_label": ["S1"],
            "nuc_label": [7],
            "key": ["/crops/sample_nuc_7.tif"],
            "latent_0": [0.25],
        }
    )
    merged = merge_with_VAE_df(features, vae)
    assert merged["latent_0"].tolist() == [0.25]
    assert "file_extracted" not in merged
    assert "key_extracted" not in merged


def test_correlation_profiles_remain_distinct():
    base = pd.DataFrame({"signal": [1.0, 2.0, 3.0], "signal_mean": [1.0, 2.0, 3.0]})
    default = drop_high_corr_columns(base.copy(), list(base.columns), 0.95)
    marker = drop_high_corr_columns_marker(base.copy(), list(base.columns), 0.95)
    assert "signal_mean" not in default
    assert "signal_mean" in marker


def test_dflib_operator_usage_pattern():
    operator = AdvancedOperator(pd.DataFrame({"A": [1, 2, 3]}))
    operator.add_column("B", [4, 5, 6])
    operator.filter_rows(lambda frame: frame["A"] > 1)
    assert operator.get_dataframe().to_dict("list") == {"A": [2, 3], "B": [5, 6]}
