

def project(id=1,
            name="Test Project",
            notes="",
            custom_fields=None):
    return {"id": id,
            "name": name,
            "notes": notes,
            "custom_fields": custom_fields or []}

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



