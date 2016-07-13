import re


def sql_safe_name(name):
    return re.sub("\W", "", re.sub("\s", "_", name))
