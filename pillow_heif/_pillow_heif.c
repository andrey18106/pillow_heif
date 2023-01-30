#include <Python.h>
#include "libheif/public_api.h"


#define RETURN_NONE Py_INCREF(Py_None); return Py_None;

/* =========== Functions ======== */


/* =========== Module =========== */

static int setup_module(PyObject* m) {
    PyObject* d = PyModule_GetDict(m);

    struct heif_encoder_descriptor* encoder_descriptor;
    const char* x265_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_HEVC, NULL, &encoder_descriptor, 1))
        x265_version = heif_encoder_descriptor_get_name(encoder_descriptor);
    const char* aom_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_AV1, NULL, &encoder_descriptor, 1))
        aom_version = heif_encoder_descriptor_get_name(encoder_descriptor);

    PyObject* version_dict = PyDict_New();
    PyDict_SetItemString(version_dict, "libheif", PyUnicode_FromString(heif_get_version()));
    PyDict_SetItemString(version_dict, "x265", PyUnicode_FromString(x265_version));
    PyDict_SetItemString(version_dict, "aom", PyUnicode_FromString(aom_version));

    if (PyDict_SetItemString(d, "lib_info", version_dict) < 0) {
        return -1;
    }

    return 0;
}

PyMODINIT_FUNC PyInit__pillow_heif(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_pillow_heif", /* m_name */
        NULL,           /* m_doc */
        -1,             /* m_size */
        NULL,           /* m_methods */
    };

    PyObject* m = PyModule_Create(&module_def);
    if (setup_module(m) < 0)
        return NULL;

    return m;
}
