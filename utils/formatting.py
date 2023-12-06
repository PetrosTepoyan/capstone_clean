
def myrealty_format_address(address):
    s = address
    splits = s.split(", ")
    split_count = len(splits)
    if split_count >= 3:
        s = splits[-1]
    return s