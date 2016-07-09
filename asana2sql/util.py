import string


invalid_punctuation = string.punctuation.translate(None, "_")


def sql_safe_name(name):
    return name.translate(None, invalid_punctuation).replace(" ", "_").lower()
