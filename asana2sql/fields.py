from asana2sql.Field import Field, SimpleField, SqlType


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
            self._workspace.add_user(assignee)
            return assignee.get("id", -1)
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
            return parent.get("id", -1)
        else:
            return None

class ProjectsField(Field):
    def __init__(self, workspace):
        super(ProjectsField, self).__init__(None, None)
        self._workspace = workspace

    def required_fields(self):
        return ["id", "projects.id", "projects.name"]

    def get_data_from_task(self, task):
        projects = {project["id"]: project for project in task.get("projects", [])}

        new_project_ids = set(projects.keys())
        old_project_ids = set(self._workspace.task_memberships(task["id"]))

        for project_id in new_project_ids.difference(old_project_ids):
            self._workspace.add_task_to_project(task["id"], projects[project_id]);

        for project_id in old_project_ids.difference(new_project_ids):
            self._workspace.remove_task_from_project(task["id"], project_id)


class CustomFields(Field):
    def __init__(self, workspace):
        super(CustomFields, self).__init__(None, None)
        self._workspace = workspace

    def required_fields(self):
        # NB: There's a bug in the API as of this writing such that if you
        # attempt to index fields inside the custom fields then you'll just get
        # back a list of null values instead of the requested ones.  Thus we
        # just have to request it all.
        return ["id", "custom_fields"]

    def get_data_from_task(self, task):
        custom_fields = {field["id"]: field
                for field in task.get("custom_fields", [])}
        old_fields = {row.custom_field_id: row
                for row in self._workspace.task_custom_field_values(task["id"])}

        for field_id, custom_field in custom_fields.items():
            if field_id in old_fields:
                old_field = old_fields[field_id]
                del(old_fields[field_id])
                if (custom_field["type"] == "text" and
                    custom_field.get("text_value") == old_field.text_value):
                        continue
                if (custom_field["type"] == "number" and
                    custom_field.get("number_value") == old_field.number_value):
                        continue
                if (custom_field["type"] == "enum" and
                    custom_field.get("enum_value") == old_field.enum_value):
                        continue

            self._workspace.add_custom_field_value(task["id"], custom_field)

        for field_id in old_fields:
            self._workspace.remove_custom_field_value(
                    task["id"], field_id)


class FollowersField(Field):
    def __init__(self, workspace):
        super(FollowersField, self).__init__(None, None)
        self._workspace = workspace

    def required_fields(self):
        return ["id", "followers.id", "followers.name"]

    def get_data_from_task(self, task):
        follower_ids = {follower["id"]: follower for follower in task.get("followers", [])}
        old_follower_ids = self._workspace.get_followers(task["id"])

        for follower_id, follower in follower_ids.items():
            if follower_id in old_follower_ids:
                old_follower_ids.remove(follower_id)
            else:
                self._workspace.add_follower(task["id"], follower)

        for follower_id in old_follower_ids:
            self._workspace.remove_follower(task["id"], follower_id)


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
            ParentIdField(),
            AssigneeField(workspace),
            AssigneeStatus(),
            ProjectsField(workspace),
            FollowersField(workspace),
            CustomFields(workspace),
            ]

