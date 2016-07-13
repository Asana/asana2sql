from asana2sql.field import SimpleField, SqlType


def TaskIdPrimaryKeyField():
    return SimpleField("id", SqlType.INTEGER, primary_key=True)


def NameField():
    return SimpleField("name", SqlType.STRING)


def NotesField():
    return SimpleField("notes", SqlType.TEXT)


def CompletedField():
    return SimpleField("completed", SqlType.BOOLEAN, default=False)


def CreatedAtField():
    return SimpleField("created_at", SqlType.DATETIME)


def NumHearts():
    return SimpleField("num_hearts", SqlType.INTEGER)
