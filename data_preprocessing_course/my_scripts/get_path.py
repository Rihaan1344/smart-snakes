import os
def get_path(bins = False) -> str:
    return os.path.join(os.path.dirname(os.getcwd()), "resources", ("sample_dataset.csv" if not bins else "sample_dataset_bins.csv"))