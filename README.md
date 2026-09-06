# nuclear-table-tools

Focused dataframe operations for object-level microscopy measurements. The
package covers filtering, feature selection, correlation pruning, joins between
classical and learned representations, and stateful pipeline composition.

## Install

```bash
python -m pip install .
```

## Example

```python
from nuclear_table_tools import drop_high_corr_columns, drop_low_unique_columns

feature_columns = [column for column in table if column.startswith("DAPI_")]
table = drop_low_unique_columns(table, feature_columns, unique_threshold=10)
feature_columns = [column for column in feature_columns if column in table]
table = drop_high_corr_columns(table, feature_columns, corr_threshold=0.95)
```

Join learned representations without losing the object-level identity keys:

```python
from nuclear_table_tools import merge_with_VAE_df

combined = merge_with_VAE_df(table, latent_table)
```

Compose project-specific derivations and row filters while retaining a readable
dataframe workflow:

```python
from nuclear_table_tools import AdvancedOperator

operator = AdvancedOperator(combined)
operator.add_column("DAPI_mean_to_area", combined["DAPI_mean"] / combined["area"])
operator.filter_rows(lambda frame: frame["DAPI_mean_to_area"].notna())
analysis_table = operator.get_dataframe()
```

Transformations preserve row identities and keep metadata columns alongside the
selected numeric feature matrix.
