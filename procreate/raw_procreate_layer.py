import biplist
from procreate_blend import ProcreateBlend

class RawProcreateLayer:
    # animationHeldLength     : int        
    blend                   : int        
    # bundledImagePath        : biplist.Uid
    # bundledMaskPath         : biplist.Uid
    # bundledVideoPath        : biplist.Uid
    clipped                 : bool       
    # contentsRect            : biplist.Uid
    # contentsRectValid       : bool       
    document                : biplist.Uid
    extendedBlend           : int        
    hidden                  : bool       
    locked                  : bool       
    mask                    : biplist.Uid
    name                    : biplist.Uid
    opacity                 : float      
    # perspectiveAssisted     : bool       
    preserve                : bool       
    private                 : bool       
    sizeHeight              : int        
    sizeWidth               : int        
    text                    : biplist.Uid
    textPDF                 : biplist.Uid
    # textureSet              : biplist.Uid
    # transform               : biplist.Uid
    type                    : int        
    uuid                    : biplist.Uid
    version                 : int        
    # videoTime               : biplist.Uid

    clean_name : str
    clean_uuid : str
    chunked_data : dict

    def __init__(self, data : dict):
        # self.animationHeldLength     : int         = data.get("animationHeldLength", None)
        self.blend                   : int         = data.get("blend", None)
        # self.bundledImagePath        : biplist.Uid = data.get("bundledImagePath", None)
        # self.bundledMaskPath         : biplist.Uid = data.get("bundledMaskPath", None)
        # self.bundledVideoPath        : biplist.Uid = data.get("bundledVideoPath", None)
        self.clipped                 : bool        = data.get("clipped", None)
        # self.contentsRect            : biplist.Uid = data.get("contentsRect", None)
        # self.contentsRectValid       : bool        = data.get("contentsRectValid", None)
        self.document                : biplist.Uid = data.get("document", None)
        self.extendedBlend           : int         = data.get("extendedBlend", None)
        self.hidden                  : bool        = data.get("hidden", None)
        self.locked                  : bool        = data.get("locked", None)
        self.mask                    : biplist.Uid = data.get("mask", None)
        self.name                    : biplist.Uid = data.get("name", None)
        self.opacity                 : float       = data.get("opacity", None)
        # self.perspectiveAssisted     : bool        = data.get("perspectiveAssisted", None)
        self.preserve                : bool        = data.get("preserve", None)
        self.private                 : bool        = data.get("private", None)
        self.sizeHeight              : int         = data.get("sizeHeight", None)
        self.sizeWidth               : int         = data.get("sizeWidth", None)
        self.text                    : biplist.Uid = data.get("text", None)
        self.textPDF                 : biplist.Uid = data.get("textPDF", None)
        # self.textureSet              : biplist.Uid = data.get("textureSet", None)
        self.transform               : biplist.Uid = data.get("transform", None)
        self.type                    : int         = data.get("type", None)
        self.uuid                    : biplist.Uid = data.get("UUID", None)
        self.version                 : int         = data.get("version", None)
        # self.videoTime               : biplist.Uid = data.get("videoTime", None)
    
    def blend_as_enum(self):
        return ProcreateBlend(self.extendedBlend)
