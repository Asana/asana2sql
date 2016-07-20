
py_library(
  name = "asana2sql",
  srcs = glob(["*.py"],
              exclude = ["*_test.py"]),
  deps = [],
  visibility = ["//visibility:public"],
)

py_library(
    name = "test_fixtures",
    srcs = ["test_fixtures.py"],
    deps = [],
)

py_test(
    name = "field_test",
    srcs = ["field_test.py"],
    deps = [
        ":asana2sql",
    ],
)

py_test(
    name = "fields_test",
    srcs = ["fields_test.py"],
    deps = [
        ":asana2sql",
    ],
)

py_test(
    name = "project_test",
    srcs = ["project_test.py"],
    deps = [
        ":test_fixtures",
        ":asana2sql",
    ],
)

py_test(
    name = "db_wrapper_test",
    srcs = ["db_wrapper_test.py"],
    deps = [
        ":asana2sql",
    ],
)

py_test(
    name = "workspace_test",
    srcs = ["workspace_test.py"],
    deps = [
        ":asana2sql",
    ],
)
