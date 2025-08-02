from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QVBoxLayout, QDialog, QLabel, QComboBox
import json
import os

class SettingsUi:
    dialog_box : QDialog
    layout : QVBoxLayout

    topmost_label : QLabel
    subtitle_label : QLabel

    refresh_check_checkbox : QCheckBox
    refresh_str : str = "Refresh projection on tile decompression (not recommended for speed)"
    refresh_str_tooltip : str = "Should the projection refresh when a tile finishes decompression?\n" \
                                "This has no practical use, slows import, and lags Krita quite a bit. Looks neat though."


    what_on_ori_layout : QHBoxLayout
    what_on_ori_label : QLabel
    what_on_orientation_combobox : QComboBox
    what_on_str : str = "What to do with saved orientation?"

    what_on_tooltop : str = "What should happen if the orientation suggests rotating the canvas? There's:\n" \
                            "* Always ask - Always ask after import is completed and the document is shown\n" \
                            "* Never rotate - Will never rotate regardless of orientation value\n" \
                            "* Always rotate - Will always rotate\n" \
                            "\n" \
                            "The default is always asking as during testing they don't seem to fully match up;\n" \
                            "rotation may not be needed or rotation may be needed.\n" \
                            "\n" \
                            "If orientation says to not rotate, you won't be asked regardless."

    what_on_items : list = ["Always ask me (default)", "Never rotate 'em", "Always rotate 'em"]


    how_to_background_layout : QHBoxLayout
    how_to_background_label : QLabel
    how_to_background_combobox : QComboBox
    how_to_background_label_txt : str = "How should backgrounds be done?"

    how_to_background_tooltip : str =   "How should the background colour be set, as a layer or as the dedicated property? There's:\n" \
                                        "* Set the property - This uses the document's background colour property, which is accessible\n" \
                                        "under (Image > Properties...) and (Image > Image Background Color and Opacity...)\n" \
                                        "* As a dedicated fill layer - This creates a colour fill layer at the bottom of the document\n" \
                                        "with the background colour.\n" \
                                        "\n" \
                                        "This is here to support different workflows; both do essentially the same thing, but a dedicated fill layer\n" \
                                        "is more customizable if that's desirable for you." 

    how_to_background_items : list = ["Set the property (Image > Properties...)", "As a dedicated fill layer"]


    import_icc_layout : QHBoxLayout
    import_icc_label : QLabel
    import_icc_combobox : QComboBox
    import_icc_label_txt : str = "How should unknown colour profiles be done?"

    import_icc_tooltip : str =  "How should colour profiles saved in Procreate documents be done if Krita doesn't know them? There's:\n" \
                                "* Always ask me - Asks if you want to export the ICC profile so Krita can import, or just use the default\n" \
                                "set in Krita.\n" \
                                "* Always use Krita's default, do not import - Ignores the saved ICC data if Krita doesn't know the profile,\n"\
                                "falling back onto the default profile configured in Krita.\n" \
                                "* Ask where to save profile, import - Goes right into the dialog to export the ICC profile, if a file name is\n"\
                                "not given or the dialog is cancelled, then the Krita default will be used.\n"\
                                "* Automatically save profile - The profile is saved in the application data of Krita under the \"colorprofile\"\n"\
                                "directory and automatically imports it.\n"\
                                "\n" \
                                "The default is to always ask; while it is more steps, it is something to try to ensure colour accuracy while\n"\
                                "maintaining user control."

    import_icc_items : list = ["Always ask me (default)", "Always use Krita's default, do not import", "Ask where to save profile, import", "Automatically save profile inside Krita, import"]

class Settings:
    refresh_projection_on_tile_complete : bool = False

    what_on_orientation : int = 0

    how_to_background : int = 0

    import_icc : int = 0

    ui : SettingsUi

    savefname : str

    def __init__(self, krita_instance):
        self.savefname = os.path.join(krita_instance.getAppDataLocation(), "_procreate_importer_settings.json")

        self.ui = SettingsUi()

        self.ui.dialog_box = QDialog(None)

        self.ui.layout = QVBoxLayout(self.ui.dialog_box)

        self.ui.topmost_label = QLabel("<h2><u>Import from Procreate Settings</u></h2>")
        self.ui.topmost_label.setAlignment(Qt.AlignCenter)
        self.ui.layout.addWidget(self.ui.topmost_label)

        self.ui.subtitle_label = QLabel(f"<font size='70%'>Changes are automatically saved and applied unless stated otherwise</font><br><font size='60%'><b>Save file:</b>\n{self.savefname}</font>")
        self.ui.subtitle_label.setAlignment(Qt.AlignCenter)
        self.ui.layout.addWidget(self.ui.subtitle_label)

        self.ui.layout.addSpacing(24)


        self.ui.what_on_ori_layout = QHBoxLayout()
        self.ui.what_on_ori_label = QLabel(self.ui.what_on_str, None)
        self.ui.what_on_ori_label.setToolTip(self.ui.what_on_tooltop)
        self.ui.what_on_ori_layout.addWidget(self.ui.what_on_ori_label)

        self.ui.what_on_orientation_combobox = QComboBox(None)
        self.ui.what_on_orientation_combobox.addItems(self.ui.what_on_items)
        self.ui.what_on_orientation_combobox.setToolTip(self.ui.what_on_tooltop)
        self.ui.what_on_orientation_combobox.currentIndexChanged.connect(self.__update_what_on_ori)
        self.ui.what_on_ori_layout.addWidget(self.ui.what_on_orientation_combobox)

        self.ui.layout.addLayout(self.ui.what_on_ori_layout)


        self.ui.how_to_background_layout = QHBoxLayout()
        self.ui.how_to_background_label = QLabel(self.ui.how_to_background_label_txt, None)
        self.ui.how_to_background_label.setToolTip(self.ui.how_to_background_tooltip)
        self.ui.how_to_background_layout.addWidget(self.ui.how_to_background_label)

        self.ui.how_to_background_combobox = QComboBox(None)
        self.ui.how_to_background_combobox.addItems(self.ui.how_to_background_items)
        self.ui.how_to_background_combobox.setToolTip(self.ui.how_to_background_tooltip)
        self.ui.how_to_background_combobox.currentIndexChanged.connect(self.__update_how_to_background)
        self.ui.how_to_background_layout.addWidget(self.ui.how_to_background_combobox)

        self.ui.layout.addLayout(self.ui.how_to_background_layout)


        self.ui.import_icc_layout = QHBoxLayout()
        self.ui.import_icc_label = QLabel(self.ui.import_icc_label_txt, None)
        self.ui.import_icc_label.setToolTip(self.ui.import_icc_tooltip)
        self.ui.import_icc_layout.addWidget(self.ui.import_icc_label)

        self.ui.import_icc_combobox = QComboBox(None)
        self.ui.import_icc_combobox.addItems(self.ui.import_icc_items)
        self.ui.import_icc_combobox.setToolTip(self.ui.import_icc_tooltip)
        self.ui.import_icc_combobox.currentIndexChanged.connect(self.__update_import_icc)
        self.ui.import_icc_layout.addWidget(self.ui.import_icc_combobox)

        self.ui.layout.addLayout(self.ui.import_icc_layout)


        self.ui.refresh_check_checkbox = QCheckBox(self.ui.refresh_str, None)
        self.ui.refresh_check_checkbox.setToolTip(self.ui.refresh_str_tooltip)
        self.ui.refresh_check_checkbox.stateChanged.connect(self.__update_refresh)
        self.ui.layout.addWidget(self.ui.refresh_check_checkbox)


        self.ui.dialog_box.setLayout(self.ui.layout)
        
        if os.path.isfile(self.savefname):
            with open(self.savefname, mode="r") as fp:
                try:
                    _d : dict = json.load(fp)
                    self.refresh_projection_on_tile_complete = _d.get("refresh", self.refresh_projection_on_tile_complete)
                    self.what_on_orientation = _d.get("orientation_ask", self.what_on_orientation)
                    self.how_to_background = _d.get("background_style", self.how_to_background)
                except json.JSONDecodeError:
                    pass # just skip
        else:
            self.__save() # create instead

    def __save(self):
        with open(self.savefname, mode="w") as fp:
            _saveables : dict = {
                "refresh": self.refresh_projection_on_tile_complete,
                "orientation_ask": self.what_on_orientation,
                "background_style": self.how_to_background,
                "unknown_colour_profile": self.import_icc
            }
            fp.write(json.dumps(_saveables))

    def __update_refresh(self, int):
        self.refresh_projection_on_tile_complete = self.ui.refresh_check_checkbox.isChecked()
        self.__save()

    def __update_what_on_ori(self, int):
        self.what_on_orientation = self.ui.what_on_orientation_combobox.currentIndex()
        self.__save()

    def __update_how_to_background(self, int):
        self.how_to_background = self.ui.how_to_background_combobox.currentIndex()
        self.__save()

    def __update_import_icc(self, int):
        self.import_icc = self.ui.import_icc_combobox.currentIndex()
        self.__save()

    def show_ui(self):
        self.ui.refresh_check_checkbox.setChecked(self.refresh_projection_on_tile_complete)
        self.ui.what_on_orientation_combobox.setCurrentIndex(self.what_on_orientation)
        self.ui.how_to_background_combobox.setCurrentIndex(self.how_to_background)
        self.ui.import_icc_combobox.setCurrentIndex(self.import_icc)
        self.ui.dialog_box.show()