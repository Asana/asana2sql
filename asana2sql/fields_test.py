import unittest
import mock

from asana2sql import fields
from asana2sql import workspace


class AssigneeFieldTestCase(unittest.TestCase):
    def test_assignee_field(self):
        ws = mock.Mock(spec=workspace.Workspace)

        user = {"id": 123, "name": "user"}

        field = fields.AssigneeField(ws)

        self.assertIsNone(field.get_data_from_task({}))
        self.assertEqual(
                field.get_data_from_task({"assignee": user}),
                123)

        ws.add_user.assert_called_once_with(user)

class ParentIdFieldTestCase(unittest.TestCase):
    def test_parent_id_field(self):
        field = fields.ParentIdField()

        self.assertIsNone(field.get_data_from_task({}))
        self.assertEqual(
                field.get_data_from_task({"parent": {"id": 123, "name": "task"}}),
                123)

class ProjectsFieldTestCase(unittest.TestCase):
    def test_no_projects(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_memberships.return_value = []

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({"id": 123}))

        ws.task_memberships.assert_called_once_with(123)

    def test_same_projects(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_memberships.return_value = [1, 2, 3]

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "projects": [
                {"id": 1, "name": "Project 1"},
                {"id": 2, "name": "Project 2"},
                {"id": 3, "name": "Project 3"},
            ]}))

        ws.task_memberships.assert_called_once_with(123)
        ws.add_task_to_project.assert_not_called()
        ws.remove_task_from_project.assert_not_called()

    def test_different_projects(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_memberships.return_value = [1, 2, 3]

        field = fields.ProjectsField(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "projects": [
                {"id": 2, "name": "Project 2"},
                {"id": 3, "name": "Project 3"},
                {"id": 4, "name": "Project 4"},
            ]}))

        ws.task_memberships.assert_called_once_with(123)
        ws.add_task_to_project.assert_called_once_with(
                123, {"id": 4, "name": "Project 4"})
        ws.remove_task_from_project.assert_called_once_with(123, 1)

class CustomFieldsFieldTestCase(unittest.TestCase):
    @staticmethod
    def mock_custom_field_value(custom_field_id, type, text_value=None,
            number_value=None, enum_value=None):
        row = mock.Mock()
        row.custom_field_id = custom_field_id
        row.type = type
        row.text_value = text_value
        row.number_value = number_value
        row.enum_value = enum_value
        return row

    def test_no_fields(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_custom_field_values.return_value = []

        field = fields.CustomFields(ws)

        self.assertIsNone(field.get_data_from_task({"id": 123}))

        ws.add_custom_field_value.assert_not_called()
        ws.remove_custom_field_value.assert_not_called()

    def test_same_fields(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_custom_field_values.return_value = [
            self.mock_custom_field_value(1, "Field 1", text_value="foo"),
            self.mock_custom_field_value(2, "Field 2", number_value=42),
            self.mock_custom_field_value(3, "Field 3", enum_value=525)]

        field = fields.CustomFields(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "custom_fields": [
                {"id": 1, "type": "text", "text_value": "foo"},
                {"id": 2, "type": "number", "number_value": 42},
                {"id": 3, "type": "enum", "enum_value": 525},
            ]}))

        ws.add_custom_field_value.assert_not_called()
        ws.remove_custom_field_value.assert_not_called()

    def test_different_fields(self):
        ws = mock.Mock(spec=workspace.Workspace)
        ws.task_custom_field_values.return_value = [
            self.mock_custom_field_value(1, "Field 1", text_value="to be removed"),
            self.mock_custom_field_value(2, "Field 2", number_value=42),
            self.mock_custom_field_value(3, "Field 3", enum_value=525),
            self.mock_custom_field_value(1, "Field 1", text_value="old value")]

        field = fields.CustomFields(ws)

        self.assertIsNone(field.get_data_from_task({
            "id": 123,
            "custom_fields": [
                {"id": 2, "type": "number", "number_value": 43},
                {"id": 3, "type": "enum", "enum_value": 625},
                {"id": 4, "type": "text", "text_value": "new value"},
                {"id": 5, "type": "text", "text_value": "new field"},
            ]}))

        ws.add_custom_field_value.assert_has_calls([
                mock.call(123, {"id": 2, "type": "number", "number_value": 43}),
                mock.call(123, {"id": 3, "type": "enum", "enum_value": 625}),
                mock.call(123, {"id": 4, "type": "text", "text_value": "new value"}),
                mock.call(123, {"id": 5, "type": "text", "text_value": "new field"}),
                ])
        ws.remove_custom_field_value.assert_called_once_with(123, 1)


if __name__ == '__main__':
    unittest.main()
