#include <Python.h>
#include "libheif/public_api.h"


#define RETURN_NONE Py_INCREF(Py_None); return Py_None;

typedef struct {
    PyObject_HEAD
    struct heif_context* ctx;               // libheif context
    size_t data_size;                       // number of bytes in `data`
    void* data;                             // encoded data if success
} LibHeifCtxWriteObject;

static PyTypeObject LibHeifCtxWrite_Type;

static void _ctx_write_dealloc(LibHeifCtxWriteObject* self) {
    heif_context_free(self->ctx);
    if (self->data != NULL)
        free(self->data);
    PyObject_Del(self);
}

/* =========== Functions ======== */


/* =========== Module =========== */

static PyTypeObject LibHeifCtxWrite_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "LibHeifCtxWrite",
    .tp_basicsize = sizeof(LibHeifCtxWriteObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)_ctx_write_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

static int setup_module(PyObject* m) {
    PyObject* d = PyModule_GetDict(m);

    if (PyType_Ready(&LibHeifCtxWrite_Type) < 0)
        return -1;

    const struct heif_encoder_descriptor* encoder_descriptor;
    const char* x265_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_HEVC, NULL, &encoder_descriptor, 1))
        x265_version = heif_encoder_descriptor_get_name(encoder_descriptor);
    const char* aom_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_AV1, NULL, &encoder_descriptor, 1))
        aom_version = heif_encoder_descriptor_get_name(encoder_descriptor);

    PyObject* version_dict = PyDict_New();
    PyDict_SetItemString(version_dict, "libheif", PyUnicode_FromString(heif_get_version()));
    PyDict_SetItemString(version_dict, "HEIF", PyUnicode_FromString(x265_version));
    PyDict_SetItemString(version_dict, "AVIF", PyUnicode_FromString(aom_version));

    if (PyDict_SetItemString(d, "lib_info", version_dict) < 0)
        return -1;

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
