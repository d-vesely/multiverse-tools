import numpy as np
import pandas as pd
from tqdm import tqdm
from user_fit import spec_list_lvl_2, spec_list_lvl_3


def generate_boot_data(specs, n_iter, data, colmap, level, save_path):
    """Generate bootstrap data.

    Arguments:
        specs -- The specifications data.
        n_iter -- The number of bootstrap iterations to run.
        data -- The meta-analytic dataset.
        colmap -- The column-map from the configuration.
        level -- The meta-analysis level (2 or 3).
        save_path -- The path to where the bootstrap data should be stored.

    Returns:
        The bootstrap data as a pandas DataFrame, with the dimensions
        (n_specs, n_iter).
    """
    # Get unique effect ID sets that make up specifications
    effect_sets = np.unique(specs["set_es"])
    effect_sets = [[int(x) for x in es.split(",")] for es in effect_sets]

    # Prepare empty matrix for samples with n_specs rows and
    # n_iter columns
    n_specs = len(specs)
    res = np.zeros((n_specs, n_iter))

    # Sample n_iter times under null hypothesis
    for col in tqdm(range(n_iter)):
        # Compute summary effects for all effect ID sets according to how-factors
        # using bootstrapped data
        if level == 2:
            boot_effects = spec_list_lvl_2(effect_sets, data, colmap)
        elif level == 3:
            boot_effects = spec_list_lvl_3(effect_sets, data, colmap)

        # Store summary effects for each specification
        res[:, col] = sorted(np.array(boot_effects).flatten())

    # Compute 95%-CI for each specification
    boot_bounds = np.quantile(res, [0.025, 0.975], axis=1)
    boot_lb = boot_bounds[0]
    boot_ub = boot_bounds[1]

    # Store bootstrapped data in data frame
    boot_data_dict = {
        "rank": [i+1 for i in range(n_specs)],
        "obs": specs["mean"],
        "boot_lb": boot_lb,
        "boot_ub": boot_ub
    }
    boot_data = pd.DataFrame(boot_data_dict)

    # Save data to CSV file
    boot_data.to_csv(save_path, index=False)

    return boot_data
