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


class AssigneeField(Field):
    def __init__(self, workspace):
        super(AssigneeField, self).__init__("assignee_id", SqlType.INTEGER)
        self._workspace = workspace

    def required_fields(self):
        return ["assignee.id", "assignee.name"]

    def get_data_from_task(self, task):
        assignee = task.get("assignee")
        if assignee:
            self._workspace.ensure_user_exists(assignee)
            return str(assignee.get("id", -1))
        else:
            return None


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
            return None

class ProjectsField(Field):
    def __init__(self, workspace):
        super(ProjectsField, self).__init__(None, None)
        self._workspace = workspace

    def required_fields(self):
        return ["id", "projects.id", "projects.name"]

    def get_data_from_task(self, task):
        projects = task.get("projects", [])

        new_project_ids = set(project["id"] for project in projects)
        old_project_ids = set(self._workspace.task_memberships(task["id"]))
        stale_project_ids = old_project_ids.difference(new_project_ids)

        for project in projects:
            self._workspace.add_task_to_project(task["id"], project);

        for project_id in stale_project_ids:
            self._workspace.remove_task_from_project(task["id"], project_id)

def default_fields(workspace):
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
            AssigneeField(workspace),
            AssigneeStatus(),
            ProjectsField(workspace),
            ParentIdField(),
            ]

