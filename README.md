<div align="center">
  <h1>Import .procreate into Krita</h1>
  <img src="/docs/splash.png" alt="Project splash" />
  <br/>
This is a Python 3 plugin for Krita that can import a Procreate project into Krita
as a new document.
</div>
<br/>

> [!NOTE]
> This is pretty identical to the Manual provided with the plugin shown within Krita.

## Installation

1. Clone with submodules (`git clone --recurse-submodules https://github.com/xubiod/import_from_procreate.git`)
  - This is the only real "complicated" part; downloading as a ZIP does not include submodules to my knowledge. Sorry :(
2. Move to under `pykrita` on a Krita install:
  - ```
    Krita install/
        pykrita/
          import_from_procreate/
            [repo files]
    ```
3. Move `import_from_procreate.desktop` **outside of the folder**:
  - ```
    Krita install/
        pykrita/
          import_from_procreate/
            [repo files]
          import_from_procreate.desktop
    ```
  - ![File list](/docs/file_list.png)
4. Restart Krita if open

The plugin should be in the list, with the name **Procreate Project Importer**:

![Plugin list](/docs/plugin_list.png)

### Overview

This plugin can import Procreate documents into Krita with complete layers with:
- Layer image data
- Layer opacity
- Clipping mask/alpha inheritance, alpha lock, visiblity and locks applied properly
- Correct<sub>1</sub> blend modes
- Groups with their proper children
- Colour profiles taken into consideration

<sub>1 - Blend modes were estimated from Krita's list, with preference towards
Photoshop blend modes. These might not be completely accurate to Procreate as a
result.</sub>

The plugin adds two items to **Tools > Scripts**:

![Menu items](/docs/menu_items.png)

- **Import \*.procreate File as New Document...** - Imports a Procreate document into Krita as a new document, using an Open File window.
- **Procreate Importer Settings...** - Settings for the plugin itself.

---

### Settings

![Settings dialog](/docs/settings.png)
Settings are heavily documented with tooltips, and are mostly relegated to how to automatically handle popups the plugin shows for certain elements of the import process.

---

### Caveats

There are some caveats with the current state of the importer that should be mentioned:

- Older Procreate documents that use LZO compression:
  - Have decompression problems
  - Take slightly longer to decompress
  
- Clipping masks/layers with inherit alpha enabled are accurate with *layer structure* but **NOT _accurate visually_**
    - You can group a paint layer with its' clipping masks above it together to get accurate visuals
    - This issue only exists because of how Krita implements this behaviour

---

### Credits

- **Xubiod** - plugin and import logic
- **Jan Kneschke** - inital pure Python LZ4 decompression logic
- **Toke Høiland-Jørgensen** - pure Python LZO decompression logic
- **Andrew Wooster**, **Kevin Kelley** - The `biplist` pip package for reading binary Apple plist files
    
