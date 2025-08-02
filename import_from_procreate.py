from krita import Krita, Extension, InfoObject, Selection
import asyncio
import math
import os
import re
import sys
import queue
import zipfile

sys.path.append(os.path.dirname(__file__) + "/biplist/")
import biplist

sys.path.append(os.path.dirname(__file__) + "/procreate")
from procreate_blend import ProcreateBlend, BLEND_MAP_TO_KRITA
from raw_procreate_document import RawProcreateDocument
from raw_procreate_group import RawProcreateGroup
from raw_procreate_layer import RawProcreateLayer

sys.path.append(os.path.dirname(__file__) + "/")
import settings
import tile_uncompress

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog

EXTENSION_ID = 'pykrita_import_from_procreate'

class ImportFromProcreate(Extension):
    """An extension for importing projects created in Procreate into Krita.

    When Krita has the extension create its actions, it will add a new item into
    Tools -> Scripts. Clicking this will open up a Open File dialog, and if it's
    a Procreate project it will load it into a new Krita document. The main function
    of this extention `import_procreate` is asynchronous and is run on the event
    loop until finished via `asyncio`.

    The default layer created by making a new document in Krita is deleted, and
    the time consuming part of the loading (decompressing Procreate layer tiles)
    is handled asynchronously. Currently, the main caveat is that this is VERY
    hard to cancel once it starts.
    """

    SIZE_RE = re.compile('^{(\d+), (\d+)}$')

    TOP_LEVEL_INDEXES : list[int]
    PLIST_DATA : dict

    settings : settings.Settings

    krita_instance : Krita
    problems : list[str] = list()

    def __init__(self, parent):
        self.krita_instance = parent
        self.settings = settings.Settings(parent)
        super().__init__(parent)

    def setup(self): pass

    def createActions(self, window):
        action_import = window.createAction(EXTENSION_ID + "_import", 'Import *.procreate File as New Document...', "tools/scripts")
        action_import.triggered.connect(self.import_full_triggered)

        action_settings = window.createAction(EXTENSION_ID + "_config", "Procreate Importer Settings...", "tools/scripts")
        action_settings.triggered.connect(self.settings.show_ui)

    def import_full_triggered(self):
        fname : str = QFileDialog.getOpenFileName(parent=None,caption="Import Procreate Project", filter="Procreate Projects (*.procreate)")[0]

        if fname is None:
            return
        
        if not fname.endswith(".procreate"):
            return

        self.TOP_LEVEL_INDEXES = list()
        self.PLIST_DATA = dict()
        asyncio.get_event_loop().run_until_complete(self.import_procreate(fname=fname))

    def get_value_uid(self, uid : biplist.Uid) -> any:
        """Helper to get an object from the property list data, with the null object being
        replaced by returning `None` instead of returning the `$null` string.

        Args:
            uid (biplist.Uid): The UID wrapper for the index. 

        Returns:
            any: An object, or `None` if there isn't one.
        """
        return (self.PLIST_DATA["$objects"][uid.integer] if uid.integer != 0 else None) if uid is not None else None

    async def import_procreate(self, fname : str):
        with zipfile.ZipFile(fname) as zf:
            with zf.open("Document.archive") as da:
                self.PLIST_DATA = biplist.readPlist(da)

            raw_document : RawProcreateDocument = RawProcreateDocument(self.PLIST_DATA.get("$objects")[self.PLIST_DATA.get("$top").get("root").integer])
            size_string : str = self.get_value_uid(raw_document.size)
            results : list[str] = self.SIZE_RE.findall(size_string)[0]

            raw_document.clean_width = int(results[1])
            raw_document.clean_height = int(results[0])

            document_name : str = self.get_value_uid(raw_document.name)
            document_background : bytes = self.get_value_uid(raw_document.backgroundColor)
            document_background_view : memoryview = memoryview(document_background).cast("f")

            background_qcolor = QColor.fromRgbF(document_background_view[0],document_background_view[1],document_background_view[2], 0.0 if raw_document.backgroundHidden else 1.0)

            colour_profile_name : str = self.get_value_uid(self.get_value_uid(raw_document.colorProfile)["SiColorProfileArchiveICCNameKey"])
            colour_profile_data : bytes = self.get_value_uid(raw_document.colorProfile)["SiColorProfileArchiveICCDataKey"]

            use_profile : str = colour_profile_name

            existing_profiles : list[str] = self.krita_instance.profiles("RGBA", "U8")

            if colour_profile_name not in existing_profiles and self.settings.import_icc != 1:
                colour_profile_box : QMessageBox = QMessageBox(None)
                colour_profile_box.setWindowTitle("Colour profile")
                colour_profile_box.setText(f"The colour profile the document is saved with is not known to Krita:\n\n{colour_profile_name}\n\nWould you like to export it so Krita can import it?")

                export_for_import_btn = colour_profile_box.addButton("   Export colour profile to use   ", QMessageBox.AcceptRole)
                colour_profile_box.addButton("   Use Krita default   ", QMessageBox.RejectRole)

                match self.settings.import_icc:
                    case 0 | 2:
                        colour_profile_box.exec()

                        if colour_profile_box.clickedButton() is export_for_import_btn:
                            icc_fname : str = QFileDialog.getSaveFileName(parent=None, caption="Save embedded ICC profile", dir=os.path.join(os.path.dirname(fname),f"{colour_profile_name}.icc"), filter="ICC Colour Profile (*.icc)")[0]

                            if icc_fname is not None and icc_fname != "":
                                with open(icc_fname, mode="wb") as icc_fp:
                                    icc_fp.write(colour_profile_data)
                                    icc_fp.flush()
                                self.krita_instance.addProfile(icc_fname)
                            else:
                                use_profile = ""
                    case 3:
                        icc_fname : str = os.path.join(self.krita_instance.getAppDataLocation(), "colorprofiles", f"{colour_profile_name}.icc")
                        with open(icc_fname, mode="wb") as icc_fp:
                            icc_fp.write(colour_profile_data)
                            icc_fp.flush()
                        self.krita_instance.addProfile(icc_fname)
                    case 1 | _:
                        use_profile = ""

            composite_uuid : str = self.get_value_uid(self.get_value_uid(raw_document.composite)["UUID"])

            krita_document = self.krita_instance.createDocument(raw_document.clean_width, raw_document.clean_height, f'procreate_{document_name}', "RGBA", "U8", use_profile, float(raw_document.SilicaDocumentArchiveDPIKey))
            krita_document.nodeByName("Background").remove()

            match self.settings.how_to_background:
                case 0:
                    krita_document.setBackgroundColor(background_qcolor)
                case 1:
                    i = InfoObject()
                    i.setProperty("color", background_qcolor)

                    s = Selection()
                    s.select(0, 0, krita_document.width(), krita_document.height(), 255)

                    background_fill = krita_document.createFillLayer("Background Fill", "color", i, s)

                    krita_document.rootNode().addChildNode(background_fill, None)
                case _:
                    pass

            self.krita_instance.activeWindow().addView(krita_document)

            layer_data_chunks = list(filter(lambda zi: ((".lz4" in zi.filename) or (".chunk" in zi.filename)) and (composite_uuid not in zi.filename), zf.infolist()))
            uuid_chunks : dict[str, list[zipfile.ZipInfo]] = dict()

            for chunk_file in layer_data_chunks:
                uuid_str : str = chunk_file.filename.split("/")[0]
                if uuid_chunks.get(uuid_str) is None:
                    uuid_chunks[uuid_str] = list()
                
                uuid_chunks[uuid_str].append(chunk_file)
            
            # PROGRESS DIALOG
            processing = QProgressDialog(f'Decompressing layer tiles... (fyi, there are {len(layer_data_chunks)} tiles.)', "Cancel import", 0, len(layer_data_chunks))
            processing.setWindowModality(QtCore.Qt.WindowModal)
            processing.setValue(0)
            processing.forceShow()

            self.TOP_LEVEL_INDEXES = list(map(lambda uid:uid.integer, self.get_value_uid(raw_document.unwrappedLayers)["NS.objects"]))
            items : queue.LifoQueue = queue.LifoQueue()

            for idx in self.TOP_LEVEL_INDEXES[::]:
                items.put((idx, krita_document.rootNode(), False))

            mutex_layer_data : asyncio.Lock = asyncio.Lock()
            background_tasks : set[asyncio.Task] = set()

            # is_next_clipped : bool = False
            # is_clipped : bool = False
            # clipping_parent : any = None
            # clipping_grandparent : any = None

            while not items.empty():
                if processing.wasCanceled():
                    items.get()
                    break

                idx, parent, is_mask = items.get()
                result = self.handle_uid_class(biplist.Uid(idx))

                match result:
                    case RawProcreateGroup():
                        result : RawProcreateGroup = result
                        layer = krita_document.createNode(result.clean_name, "grouplayer")
                        layer.setBlendingMode("passthrough")
                        layer.setCollapsed(result.isCollapsed)
                        layer.setInheritAlpha(result.isClipped)
                        layer.setLocked(result.isLocked)
                        layer.setOpacity(int(result.opacity * 255))
                        layer.setVisible(not result.isHidden)

                        for child_uid in result.clean_children[::]:
                            items.put((child_uid, layer, False))
                    case RawProcreateLayer():
                        result : RawProcreateLayer = result
                        channels : int = 4
                        if not is_mask:
                            layer = krita_document.createNode(result.clean_name, "paintlayer")
                            layer.setAlphaLocked(result.preserve)
                            layer.setBlendingMode(BLEND_MAP_TO_KRITA[ProcreateBlend(result.extendedBlend)])
                            layer.setInheritAlpha(result.clipped)
                            # is_clipped = result.clipped
                            layer.setLocked(result.locked)
                            layer.setOpacity(int(result.opacity * 255))
                            layer.setVisible(not result.hidden)

                            if result.mask.integer != 0:
                                items.put((result.mask.integer, layer, True))
                        else:
                            channels = 1
                            layer = krita_document.createTransparencyMask(result.clean_name)
                            layer.setVisible(not result.hidden)
                            layer.setPixelData(bytearray([0xFF] * raw_document.clean_width * raw_document.clean_height), 0, 0, raw_document.clean_width, raw_document.clean_height)
                        
                        task = asyncio.create_task(tile_uncompress.decompress_layer_data(zf, uuid_chunks[result.clean_uuid], raw_document, layer, processing, self.problems, mutex_layer_data, krita_document, self.settings.refresh_projection_on_tile_complete, channels=channels))
                        background_tasks.add(task)
                        task.add_done_callback(background_tasks.discard)
                    case _:
                        continue

                # if not items.empty():
                #     next_idx, next_parent, next_is_mask = items.get()
                #     next_result = self.handle_uid_class(biplist.Uid(next_idx))
                #     is_next_clipped = False
                #     if isinstance(next_result, RawProcreateLayer):
                #         is_next_clipped = next_result.clipped
                #         if is_next_clipped:
                #             clipping_parent = krita_document.createNode(f"Clipping_{result.clean_name}", "grouplayer")
                #             clipping_parent.setBlendingMode("passthrough")
                #             clipping_grandparent = next_parent
                #     items.put((next_idx, next_parent, next_is_mask))
                
                # if (is_next_clipped or is_clipped) and clipping_parent is not None:
                #     success = clipping_parent.addChildNode(layer, None)
                #     if not success:
                #         self.problems.append(f"Layer \"{layer.name()}\" was not added to clipping group")
                #     if not is_next_clipped:
                #         clipping_grandparent.addChildNode(clipping_parent, None)
                #         clipping_parent = None
                #     continue

                parent.addChildNode(layer, None)
            
            await asyncio.wait(background_tasks)

            krita_document.refreshProjection()

            if len(self.problems) > 0:
                problems_str : str = ""
                for problem in self.problems:
                    problems_str = f'{problem}\n'

                QMessageBox.about(None, "Ooops!", f'There was something that went wrong while importing:\n\n{problems_str}')
            
            processing.reset()

            if raw_document.orientation > 1:
                auto_rotate : QMessageBox = QMessageBox(None)

                radians : float = math.pi * ((raw_document.orientation - 1) / 2)
                degrees : int = math.floor((radians * 180) / math.pi)

                if degrees > 180:
                    degrees = degrees - 360

                if self.settings.what_on_orientation == 0:
                    auto_rotate.setWindowTitle("Apply orientation?")
                    auto_rotate.setText(f"This document has an orientation value that would rotate it by {abs(degrees)} degrees to the {'right' if abs(degrees) == degrees else 'left'}.\n\nDo you want to have this applied now?")

                    do_rotate = auto_rotate.addButton("  Rotate for me  ", QMessageBox.ApplyRole)
                    auto_rotate.addButton("  Looks fine to me  ", QMessageBox.RejectRole)

                    auto_rotate.exec()

                if self.settings.what_on_orientation == 2 or (self.settings.what_on_orientation == 0 and auto_rotate.clickedButton() is do_rotate):
                    krita_document.rotateImage(radians)
                    krita_document.refreshProjection()
            
            if raw_document.flippedHorizontally or raw_document.flippedVertically:
                flip : QMessageBox = QMessageBox(None)
                flip.setWindowTitle("Flipped document")
                flip.setText(f"The document has a flip toggle on:\n\n{'Flipped horizontally' if raw_document.flippedHorizontally else ''}{'Flipped vertically' if raw_document.flippedVertically else ''}\n\nCurrently, this cannot be applied automatically to the entire document.")

                flip.addButton("   Ok   ", QMessageBox.AcceptRole)

                flip.exec()

    def handle_uid_class(self, uid : biplist.Uid) -> RawProcreateLayer | RawProcreateGroup | None:
        _itm = self.get_value_uid(uid)
        _class = self.get_value_uid(_itm["$class"])["$classname"]
        match _class:
            case 'SilicaGroup':
                _group : RawProcreateGroup = RawProcreateGroup(_itm)
                _group.clean_children : list[int] = list(map(lambda uid:uid.integer, self.get_value_uid(_group.children)['NS.objects']))
                _group.clean_name = str(self.get_value_uid(_group.name))
                return _group
            case 'SilicaLayer':
                _layer : RawProcreateLayer = RawProcreateLayer(self.get_value_uid(uid))
                _layer.clean_name = str(self.get_value_uid(_layer.name))
                _layer.clean_uuid = self.get_value_uid(_layer.uuid)
                if _layer.clean_name is None:
                    _text = self.get_value_uid(_layer.text)
                    _as_string = self.get_value_uid(_text['attributedString'])
                    _ns_string : str = self.get_value_uid(_as_string['NSString'])
                    _layer.clean_name = _ns_string["NS.string"]
                return _layer
            case _:
                return None
