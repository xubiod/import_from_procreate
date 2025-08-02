import biplist

class RawProcreateGroup:
    animationHeldLength : int        
    children            : biplist.Uid
    document            : biplist.Uid
    isClipped           : bool       
    isCollapsed         : bool       
    isHidden            : bool       
    isLocked            : bool       
    isPrivate           : bool       
    name                : biplist.Uid
    opacity             : float      

    clean_name     : str
    clean_children : list
    
    def __init__(self, data : dict):
        self.animationHeldLength : int          = data.get("animationHeldLength", None)
        self.children            : biplist.Uid  = data.get("children", None)
        self.document            : biplist.Uid  = data.get("document", None)
        self.isClipped           : bool         = data.get("isClipped", None)
        self.isCollapsed         : bool         = data.get("isCollapsed", None)
        self.isHidden            : bool         = data.get("isHidden", None)
        self.isLocked            : bool         = data.get("isLocked", None)
        self.isPrivate           : bool         = data.get("isPrivate", None)
        self.name                : biplist.Uid  = data.get("name", None)
        self.opacity             : float        = data.get("opacity", None)