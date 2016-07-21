import mock


def project(id=1,
            name="Test Project"):
    return {"id": id,
            "name": name}

def user(id=1, name="Test User"):
    return {"id": id,
            "name": name}

def task(id=2,
         name="Test Task",
         notes="",
         completed="",
         created_at=None,
         completed_at=None,
         due_on=None,
         due_at=None,
         parent=None,
         hearts=None,
         tags=None,
         custom_fields=None):
    tags = tags or []
    hearts = hearts or []
    custom_fields = custom_fields or []
    num_hearts = len(hearts)
    return {"id": id,
            "name": name,
            "notes": notes,
            "completed": completed,
            "created_at": created_at,
            "completed_at": completed_at,
            "due_on": due_on,
            "due_at": due_at,
            "parent": parent,
            "num_hearts": num_hearts,
            "hearts": hearts,
            "tags": tags,
            "custom_fields": custom_fields}

def row(**kwargs):
    row = mock.MagicMock()
    column_definitions = []
    row.__getitem__.side_effect = lambda i: kwargs.values()[i]
    for k, v in kwargs.iteritems():
        column_definitions.append((k, None, None, None, None, None, None))
        setattr(row, k, v)
    row.cursor_description = column_definitions
    return row
