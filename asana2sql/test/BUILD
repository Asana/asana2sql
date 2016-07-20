py_library(
    name = "fixtures",
    srcs = ["fixtures.py"],
    deps = [],
)

py_test(
    name = "field_test",
    srcs = ["field_test.py"],
    deps = [
        ":fixtures",
        "//asana2sql",
    ],
)

py_test(
    name = "fields_test",
    srcs = ["fields_test.py"],
    deps = [
        ":fixtures",
        "//asana2sql",
    ],
)

py_test(
    name = "project_test",
    srcs = ["project_test.py"],
    deps = [
        ":fixtures",
        "//asana2sql",
    ],
)

py_test(
    name = "db_wrapper_test",
    srcs = ["db_wrapper_test.py"],
    deps = [
        ":fixtures",
        "//asana2sql",
    ],
)
