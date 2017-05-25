# This file does the appropriate transformations to the data before it is processed

import pandas as pd

def keysRenaming(raw,translate_xls):
    output = {}
    headers = pd.read_excel(translate_xls)
    # Create a list of each column, then a dictonary which is acting as the translotor.
    old_selected = raw.keys()
    old = headers['ORIGINAL_HEADER']
    new = headers['NEW_HEADER']
    for old_title in old_selected:
        idx = pd.Index(old).get_loc(old_title)
        output[new[idx]] = old_title
    return output


def columnSelection(raw):
    # This function is used to input what columns of the dataset should be kept, so that only those are retained.
    columns_to_keep = [

    ]