import wx

from src.wizard.view.clsAffiliationPanel\
    import AffiliationPanelView
from src.common.functions import wxdate2pydate
from odm2api.ODM2.models import Affiliations

class AffiliationPanel(AffiliationPanelView):
    def __init__(self, parent):
        super(AffiliationPanel, self).__init__(parent)
        self.parent = parent
        self.Bind(wx.EVT_SHOW, self.onShow)

        read = self.parent.database.getReadSession()
        

    def createAffiliation(self):
        write = self.parent.database.getWriteSession()
        
        personID = self.data["Person"]["ID"]
        orgID = self.data["Organization"]["ID"]
        if not orgID:
            orgID = None
        else:
            orgID = int(orgID)
        affEmail = str(self.textEmail.GetValue())
        affStart = wxdate2pydate(self.dateStart.GetValue())
        affPhone = None
        if str(self.textPhone.GetValue()) != "":
            affPhone = str(self.textPhone.GetValue())
        affAddr = None
        if str(self.textAddr.GetValue()) != "":
            affAddr = str(self.textAddr.GetValue())
        affLink = None
        if str(self.textLink.GetValue()) != "":
            affLink = str(self.textLink.GetValue())
        affIsContact = self.checkPrimary.GetValue()
        affEnd = None

        aff = Affiliations(PersonID=int(personID),
            OrganizationID=orgID,
            PrimaryEmail=affEmail,
            PrimaryPhone=affPhone,
            PrimaryAddress=affAddr,
            PersonLink=affLink,
            IsPrimaryOrganizationContact=affIsContact,
            AffiliationStartDate=affStart,
            AffiliationEndDate=affEnd)
        affiliation = write.createAffiliation(aff) # TODO figure out how to have empty dates.
        
        print affiliation
        return affiliation

    def getData(self):
        return {}

    def onShow(self, event):
        self.parent.btnNext.Enable(True)
        if event.GetShow() is True:
            self.data = self.parent.getSelections()
            
            self.textPerson.SetValue(self.data["Person"]["Name"])
            self.textOrg.SetValue(self.data["Organization"]["Name"])

        event.Skip()
  
    def enable(self, event):
        self.parent.btnNext.Enable(True)
        event.Skip()
    
    def disable(self, event):
        self.parent.btnNext.Enable(False)
        event.Skip()

