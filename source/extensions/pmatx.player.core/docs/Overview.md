# Overview

An example C++ extension that can be used as a reference/template for creating new extensions.

Demonstrates how to reflect C++ code using pybind11 so that it can be called from Python code.

The IPmatxPlayerCoreInterface located in `include/pmatx/player/core/IPmatxPlayerCoreInterface.h` is:
- Implemented in `plugins/pmatx.player.core/ExamplePybindExtension.cpp`.
- Reflected in `bindings/python/pmatx.player.core/ExamplePybindBindings.cpp`.
- Accessed from Python in `python/tests/test_pybind_example.py` via `python/impl/example_pybind_extension.py`.


# C++ Usage Examples


## Defining Pybind Module


```
PYBIND11_MODULE(_pmatx_player_core_lib, m)
{
    using namespace pmatx::player::core
;

    m.doc() = "pybind11 pmatx.player.core bindings";

    carb::defineInterfaceClass<IPmatxPlayerCoreInterface>(
        m, "IPmatxPlayerCoreInterface", "acquire_bound_interface", "release_bound_interface")
        .def("register_bound_object", &IPmatxPlayerCoreInterface::registerPmatxPlayerCoreObject,
             R"(
             Register a bound object.

             Args:
                 object: The bound object to register.
             )",
             py::arg("object"))
        .def("deregister_bound_object", &IPmatxPlayerCoreInterface::deregisterPmatxPlayerCoreObject,
             R"(
             Deregister a bound object.

             Args:
                 object: The bound object to deregister.
             )",
             py::arg("object"))
        .def("find_bound_object", &IPmatxPlayerCoreInterface::findPmatxPlayerCoreObject, py::return_value_policy::reference,
             R"(
             Find a bound object.

             Args:
                 id: Id of the bound object.

             Return:
                 The bound object if it exists, an empty object otherwise.
             )",
             py::arg("id"))
        /**/;

    py::class_<IPmatxPlayerCoreObjectInterface, carb::ObjectPtr<IPmatxPlayerCoreObjectInterface>>(m, "IPmatxPlayerCoreObjectInterface")
        .def_property_readonly("id", &IPmatxPlayerCoreObjectInterface::getId, py::return_value_policy::reference,
            R"(
             Get the id of this bound object.

             Return:
                 The id of this bound object.
             )")
        /**/;

    py::class_<PythonPmatxPlayerCoreObject, IPmatxPlayerCoreObjectInterface, carb::ObjectPtr<PythonPmatxPlayerCoreObject>>(m, "PmatxPlayerCoreObject")
        .def(py::init([](const char* id) { return PythonPmatxPlayerCoreObject::create(id); }),
             R"(
             Create a bound object.

             Args:
                 id: Id of the bound object.

             Return:
                 The bound object that was created.
             )",
             py::arg("id"))
        .def_readwrite("property_int", &PythonPmatxPlayerCoreObject::m_memberInt,
             R"(
             Int property bound directly.
             )")
        .def_readwrite("property_bool", &PythonPmatxPlayerCoreObject::m_memberBool,
             R"(
             Bool property bound directly.
             )")
        .def_property("property_string", &PythonPmatxPlayerCoreObject::getMemberString, &PythonPmatxPlayerCoreObject::setMemberString, py::return_value_policy::reference,
             R"(
             String property bound using accessors.
             )")
        .def("multiply_int_property", &PythonPmatxPlayerCoreObject::multiplyIntProperty,
             R"(
             Bound fuction that accepts an argument.

             Args:
                 value_to_multiply: The value to multiply by.
             )",
             py::arg("value_to_multiply"))
        .def("toggle_bool_property", &PythonPmatxPlayerCoreObject::toggleBoolProperty,
             R"(
             Bound fuction that returns a value.

             Return:
                 The toggled bool value.
             )")
        .def("append_string_property", &PythonPmatxPlayerCoreObject::appendStringProperty, py::return_value_policy::reference,
             R"(
             Bound fuction that accepts an argument and returns a value.

             Args:
                 value_to_append: The value to append.

             Return:
                 The new string value.
             )",
             py::arg("value_to_append"))
        /**/;
}
```
