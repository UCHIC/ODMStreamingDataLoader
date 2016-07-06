import wx

from src.wizard.view.clsAddSpatialReferences \
    import NewSpatialReferenceView
from odm2api.ODM2.models import SpatialReferences

class NewSpatialReferenceController(NewSpatialReferenceView):
    def __init__(self, parent, database):
        super(NewSpatialReferenceController, self).__init__(parent)
        self.parent = parent
        self.database = database
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.m_sdbSizer10OK.Bind(wx.EVT_BUTTON, self.onOK)

    def onOK(self, event):
        # Try to validate the form.
        if not self.Validate():
            self.Refresh()
            return
 
        write = self.database.getWriteSession()
        
        name = str(self.textName.GetValue())
        code = None
        if str(self.textCode.GetValue()) != "":
            code = str(self.textCode.GetValue())
        desc = None
        if str(self.textDesc.GetValue()) != "":
            desc = str(self.textDesc.GetValue())
        
        try:
            srs=SpatialReferences(SRSCode=code,
                SRSName=name,
                SRSDescription=desc)
            write.createSpatialReference(srs)
        except Exception:
            wx.MessageBox("Error creating spatial reference.", "API Error!")

        event.Skip()

    def onShow(self, event):
        event.Skip()
  
    def enable(self, event):
        self.parent.btnNext.Enable(True)
        event.Skip()
    
    def disable(self, event):
        self.parent.btnNext.Enable(False)
        event.Skip()

