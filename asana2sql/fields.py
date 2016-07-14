from asana2sql.field import Field, SimpleField, SqlType


def TaskIdPrimaryKeyField():
    return SimpleField("id", SqlType.INTEGER, primary_key=True)


def NameField():
    return SimpleField("name", SqlType.STRING)


def NotesField():
    return SimpleField("notes", SqlType.TEXT)


def CreatedAtField():
    return SimpleField("created_at", SqlType.DATETIME)


def ModifiedAtField():
    return SimpleField("modified_at", SqlType.DATETIME)


def CompletedField():
    return SimpleField("completed", SqlType.BOOLEAN, default=False)


def CompletedAtField():
    return SimpleField("completed_at", SqlType.DATETIME)


def DueOnField():
    return SimpleField("due_on", SqlType.DATE)


def DueAtField():
    return SimpleField("due_at", SqlType.DATETIME)


def NumHearts():
    return SimpleField("num_hearts", SqlType.INTEGER, default=0)


class AssigneeIdField(Field):
    def __init__(self):
        super(AssigneeIdField, self).__init__("assignee_id", SqlType.INTEGER)

    def required_fields(self):
        return ["assignee"]

    def get_data_from_task(self, task):
        assignee = task.get("assignee")
        if assignee:
            return str(assignee.get("id", -1))
        else:
            return "NULL"


def AssigneeStatus():
    return SimpleField("assignee_status", SqlType.STRING)

class ParentIdField(Field):
    def __init__(self):
        super(ParentIdField, self).__init__("parent_id", SqlType.INTEGER)

    def required_fields(self):
        return ["parent"]

    def get_data_from_task(self, task):
        parent = task.get("parent")
        if parent:
            return str(parent.get("id", -1))
        else:
            return "NULL"


def default_fields():
    return [TaskIdPrimaryKeyField(),
            NameField(),
            NotesField(),
            CreatedAtField(),
            ModifiedAtField(),
            CompletedField(),
            CompletedAtField(),
            DueOnField(),
            DueAtField(),
            NumHearts(),
            AssigneeIdField(),
            AssigneeStatus(),
            ParentIdField(),
            ]

