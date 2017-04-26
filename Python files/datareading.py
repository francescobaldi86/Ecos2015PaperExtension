# This file does the appropriate transformations to the data before it is processed

import re

def keysRenaming(raw):
    # This function renames the keys of the dataset appropriately, so that it is easier to read them later on
    raw_keys = raw.keys()
    new_keys = []
    for idx in range(len(raw_keys)):
        key = raw_keys[idx]
        key = re.sub(" ","_",key)  # Substitutes spaces with underscores
        key = re.sub("M.*:[0-9]{4}", "", key)  # Removes the beginning of the line, with the "MAIN" text and the number
        key = re.sub("_Ave.*_900", "", key)  #  the last part, with "Average"
        key = re.sub("_Raw.*_900", "", key)  # Removes the last part, with "Raw data"
        key = re.sub(":av_", "", key)  # Removes the "av" particle in the beginning (when it exists)
        new_keys.append(key)  # Reassigning the key
    raw.columns = new_keys
    return raw


def columnSelection(raw):
    # This function is used to input what columns of the dataset should be kept, so that only those are retained.
    columns_to_keep = [

    ]