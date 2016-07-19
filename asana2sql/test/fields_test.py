import unittest
from mock import Mock

from asana2sql import fields


class FieldTestCase(unittest.TestCase):
    def test_assignee_field(self):
        ws = Mock()

        user = {"id": 123, "name": "user"}

        field = fields.AssigneeField(ws)

        self.assertIsNone(field.get_data_from_task({}))
        self.assertEqual(
                field.get_data_from_task({"assignee": user}),
                123)

        ws.ensure_user_exists.assert_called_with(user)

    def test_parent_id_field(self):
        field = fields.ParentIdField()

        self.assertIsNone(field.get_data_from_task({}))
        self.assertEqual(
                field.get_data_from_task({"parent": {"id": 123, "name": "task"}}),
                123)

    def test_projects_field_no_projects(self):
        ws = Mock()
        ws.task_memberships.return_value = []

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({"id": 123}))

        ws.task_memberships.assert_called_with(123)

    def test_projects_field_same_projects(self):
        ws = Mock()
        ws.task_memberships.return_value = [1, 2, 3]

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "projects": [
                {"id": 1, "name": "Project 1"},
                {"id": 2, "name": "Project 2"},
                {"id": 3, "name": "Project 3"},
            ]}))

        ws.task_memberships.assert_called_with(123)
        ws.add_task_to_project.assert_not_called()
        ws.remove_task_from_project.assert_not_called()

    def test_projects_field_different_projects(self):
        ws = Mock()
        ws.task_memberships.return_value = [1, 2, 3]

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "projects": [
                {"id": 2, "name": "Project 2"},
                {"id": 3, "name": "Project 3"},
                {"id": 4, "name": "Project 4"},
            ]}))

        ws.task_memberships.assert_called_with(123)
        ws.add_task_to_project.assert_called_with(
                123, {"id": 4, "name": "Project 4"})
        ws.remove_task_from_project.assert_called_with(123, 1)


if __name__ == '__main__':
    unittest.main()
