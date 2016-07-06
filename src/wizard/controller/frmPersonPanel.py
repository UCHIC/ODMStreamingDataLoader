import wx

from src.wizard.view.clsPersonPanel\
    import PersonPanelView
from odm2api.ODM2.models import People

class PersonPanel(PersonPanelView):
    def __init__(self, parent):
        super(PersonPanel, self).__init__(parent)
        self.parent = parent
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.m_comboBox13.Bind(wx.EVT_COMBOBOX, self.onPrePerson)

        self.parent.btnNext.Enable(True)
        
        read = self.parent.database.getReadSession()
    
        people = read.getPeople()
        self.people = {}
        [self.people.update({p.PersonFirstName + " " + p.PersonLastName:p.PersonID})\
            for p in people]
    
        if not self.people:
            self.m_comboBox13.Enable(False)
        else:
            self.m_comboBox13.AppendItems(self.people.keys()) 

    def getData(self):
        if str(self.m_comboBox13.GetStringSelection()) == '':
            write = self.parent.database.getWriteSession()
            
            first = str(self.textFirst.GetValue())
            last = str(self.textLast.GetValue())
            middle = str(self.textMiddle.GetValue())
            person = People(PersonFirstName=first,
                PersonLastName=last, PersonMiddleName=middle)
            person = write.createPerson(person)

            self.personID = person.PersonID
            self.personName = first + " " + middle + " " + last

        return dict({"Person":{"Name":self.personName, "ID":self.personID}})

    def onPrePerson(self, event):
        self.textFirst.SetValidator(wx.DefaultValidator)
        self.textLast.SetValidator(wx.DefaultValidator)

        self.personID = self.people[self.m_comboBox13.GetStringSelection()]
        self.personName = self.m_comboBox13.GetStringSelection()
        
        event.Skip()

    def Validate(self):
        if super(PersonPanel, self).Validate():
            return True
        return False

    def onShow(self, event):
        event.Skip()
  
    def enable(self, event):
        self.parent.btnNext.Enable(True)
        event.Skip()
    
    def disable(self, event):
        self.parent.btnNext.Enable(False)
        event.Skip()

