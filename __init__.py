from .import_from_procreate import ImportFromProcreate

app = Krita.instance()  # noqa: F821
extension = ImportFromProcreate(parent = app)
app.addExtension(extension)
