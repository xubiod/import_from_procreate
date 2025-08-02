import biplist

class RawProcreateDocument:
    animation                         : biplist.Uid
    authorName                        : biplist.Uid
    backgroundColor                   : biplist.Uid
    backgroundColorHSBA               : biplist.Uid
    backgroundHidden                  : bool       
    colorProfile                      : biplist.Uid
    composite                         : biplist.Uid
    drawingguide                      : biplist.Uid
    faceBackgroundHidden              : bool       
    featureSet                        : int        
    flippedHorizontally               : bool       
    flippedVertically                 : bool       
    isFirstItemAnimationForeground    : bool       
    isLastItemAnimationBackground     : bool       
    lastTextStyling                   : biplist.Uid
    layers                            : biplist.Uid
    mask                              : biplist.Uid
    name                              : biplist.Uid
    orientation                       : int        
    primaryItem                       : biplist.Uid
    reference3D                       : bool       
    referenceAnchor                   : int        
    referenceCorner                   : int        
    referenceDocked                   : bool       
    referenceOrientation              : int        
    referenceSize                     : biplist.Uid
    referenceVisibility               : bool       
    selectedLayer                     : biplist.Uid
    selectedSamplerLayer              : biplist.Uid
    SilicaDocumentArchiveDPIKey       : float      
    SilicaDocumentArchiveUnitKey      : int        
    SilicaDocumentTrackedTimeKey      : float      
    SilicaDocumentVideoPurgedKey      : bool       
    SilicaDocumentVideoSegmentInfoKey : biplist.Uid
    size                              : biplist.Uid
    solo                              : biplist.Uid
    strokeCount                       : biplist.Uid
    tileSize                          : int        
    unwrappedLayers                   : biplist.Uid
    userSavedSelectionMasks           : biplist.Uid
    version                           : int        
    videoCodec2020Key                 : int        
    videoEnabled                      : bool       
    videoQualityKey                   : biplist.Uid
    videoResolutionKey                : biplist.Uid

    clean_width  : int
    clean_height : int

    def __init__(self, data : dict):
        self.animation                         : biplist.Uid = data.get("animation", None)
        self.authorName                        : biplist.Uid = data.get("authorName", None)
        self.backgroundColor                   : biplist.Uid = data.get("backgroundColor", None)
        self.backgroundColorHSBA               : biplist.Uid = data.get("backgroundColorHSBA", None)
        self.backgroundHidden                  : bool        = data.get("backgroundHidden", None)
        self.colorProfile                      : biplist.Uid = data.get("colorProfile", None)
        self.composite                         : biplist.Uid = data.get("composite", None)
        self.drawingguide                      : biplist.Uid = data.get("drawingguide", None)
        self.faceBackgroundHidden              : bool        = data.get("faceBackgroundHidden", None)
        self.featureSet                        : int         = data.get("featureSet", None)
        self.flippedHorizontally               : bool        = data.get("flippedHorizontally", None)
        self.flippedVertically                 : bool        = data.get("flippedVertically", None)
        self.isFirstItemAnimationForeground    : bool        = data.get("isFirstItemAnimationForeground", None)
        self.isLastItemAnimationBackground     : bool        = data.get("isLastItemAnimationBackground", None)
        self.lastTextStyling                   : biplist.Uid = data.get("lastTextStyling", None)
        self.layers                            : biplist.Uid = data.get("layers", None)
        self.mask                              : biplist.Uid = data.get("mask", None)
        self.name                              : biplist.Uid = data.get("name", None)
        self.orientation                       : int         = data.get("orientation", None)
        self.primaryItem                       : biplist.Uid = data.get("primaryItem", None)
        self.reference3D                       : bool        = data.get("reference3D", None)
        self.referenceAnchor                   : int         = data.get("referenceAnchor", None)
        self.referenceCorner                   : int         = data.get("referenceCorner", None)
        self.referenceDocked                   : bool        = data.get("referenceDocked", None)
        self.referenceOrientation              : int         = data.get("referenceOrientation", None)
        self.referenceSize                     : biplist.Uid = data.get("referenceSize", None)
        self.referenceVisibility               : bool        = data.get("referenceVisibility", None)
        self.selectedLayer                     : biplist.Uid = data.get("selectedLayer", None)
        self.selectedSamplerLayer              : biplist.Uid = data.get("selectedSamplerLayer", None)
        self.SilicaDocumentArchiveDPIKey       : float       = data.get("SilicaDocumentArchiveDPIKey", None)
        self.SilicaDocumentArchiveUnitKey      : int         = data.get("SilicaDocumentArchiveUnitKey", None)
        self.SilicaDocumentTrackedTimeKey      : float       = data.get("SilicaDocumentTrackedTimeKey", None)
        self.SilicaDocumentVideoPurgedKey      : bool        = data.get("SilicaDocumentVideoPurgedKey", None)
        self.SilicaDocumentVideoSegmentInfoKey : biplist.Uid = data.get("SilicaDocumentVideoSegmentInfoKey", None)
        self.size                              : biplist.Uid = data.get("size", None)
        self.solo                              : biplist.Uid = data.get("solo", None)
        self.strokeCount                       : biplist.Uid = data.get("strokeCount", None)
        self.tileSize                          : int         = data.get("tileSize", None)
        self.unwrappedLayers                   : biplist.Uid = data.get("unwrappedLayers", None)
        self.userSavedSelectionMasks           : biplist.Uid = data.get("userSavedSelectionMasks", None)
        self.version                           : int         = data.get("version", None)
        self.videoCodec2020Key                 : int         = data.get("videoCodec2020Key", None)
        self.videoEnabled                      : bool        = data.get("videoEnabled", None)
        self.videoQualityKey                   : biplist.Uid = data.get("videoQualityKey", None)
        self.videoResolutionKey                : biplist.Uid = data.get("videoResolutionKey", None)