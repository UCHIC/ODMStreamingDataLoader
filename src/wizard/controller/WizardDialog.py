import wx
from src.wizard.controller.frmSampFeatSelectPanel import SampFeatSelectPanel
from src.wizard.controller.frmVariableSelectPanel import VariableSelectPanel
from src.wizard.controller.frmUnitSelectPanel import UnitSelectPanel
from src.wizard.controller.frmProcLevelSelectPanel import ProcLevelSelectPanel
from src.wizard.controller.frmActionsSelectPanel import ActionsSelectPanel
# from src.wizard.view.clsResultPage import ResultPageView
from src.wizard.controller.frmResultSummaryPanel import ResultSummaryPanel
from datetime import datetime


class WizardDialog(wx.Dialog):
    def __init__(self, parent, database=None, title="Wizard Dialog",
                 result=None,
                 size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):

        self.existingResult = result
        pre = wx.PreDialog()
        pre.Create(parent, wx.ID_ANY, title, pos, size, style)
        self.PostCreate(pre)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.pnlSizer = wx.BoxSizer(wx.VERTICAL)
        self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.pnlList = []
        self.currentPnl = None
        self.database = database

        self.addButtons()
        self.centerSelf()
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.returnValue = wx.ID_ANY
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.Destroy()

    def centerSelf(self):
        self.CenterOnParent()

    def addButtons(self):
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.btnNext = wx.Button(self, wx.ID_ANY, "Finish")
        self.btnPrev = wx.Button(self, wx.ID_ANY, "< Back")

        self.btnSizer.Add(self.btnCancel, 0, 
                          wx.ALL|wx.ALIGN_RIGHT, 5)
        self.btnSizer.Add(self.btnPrev, 0, 
                          wx.ALL|wx.ALIGN_RIGHT, 5)
        self.btnSizer.Add(self.btnNext, 0, 
                          wx.ALL|wx.ALIGN_RIGHT, 5)

        self.mainSizer.Add(self.pnlSizer, 1, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(self.btnSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 5)

        self.btnPrev.Enable(False)
        self.btnNext.Enable(False)
        self.btnNext.Bind(wx.EVT_BUTTON, self.onFinish)
        self.btnPrev.Bind(wx.EVT_BUTTON, self.onPrev)
    
    def addPage(self, pnl, **kwargs):
        newPnl = pnl(self, existing_result= self.existingResult, **kwargs)
        newPnl.Hide()
        self.pnlList.append(newPnl)
        self.pnlSizer.Add(newPnl, 1, wx.ALL|wx.EXPAND, 5)
        self.CenterOnParent()

        if len(self.pnlList) == 1:
            self.btnNext.Unbind(wx.EVT_BUTTON)
            self.btnNext.SetLabel("Next >")
            self.btnNext.Bind(wx.EVT_BUTTON, self.onNext)
    
    def getSelections(self):
        data = {}
        i = 0
        for pnl in self.pnlList:
            try:
                data[i] = pnl.list_ctrl.GetSelectedObject()
                i = i + 1
            except AttributeError:
                continue
        return data

    def ShowModal(self):
        if self.pnlList:
            self.currentPnl = self.pnlList[0]
            self.currentPnl.Show()
        self.mainSizer.Fit(self)
        self.CenterOnParent()
        super(WizardDialog, self).ShowModal()
        return self.returnValue

    # ********************** #
    # *** Event Handlers *** #
    # ********************** #

    def onFinish(self, event):
        # self.result = self.pnlList[-1].createResult()
        #
        # if self.existingResult:
        #     print self.existingResult
        # else:
        #     if self.result:
        #         self.returnValue = wx.ID_OK
        #         self.Close()
        #
        # event.Skip()
        if self.existingResult is None:
            self.__create_new_result()
        else:
            self.__update_existing_result()

    def __create_new_result(self):
        self.result = self.pnlList[-1].createResult()
        if self.result:
            self.returnValue = wx.ID_OK
            self.Close()

    def __update_existing_result(self):

        if not isinstance(self.currentPnl, ResultSummaryPanel):
            raise Exception("self.currentPanel must be of type ResultSummaryPanel")

        result = self.existingResult

        result.SampledMediumCV = self.currentPnl.comboSamp.GetValue()
        result.AggregationStatisticCV = self.currentPnl.comboAgg.GetValue()

        if self.currentPnl.comboStatus.GetValue() != "":
            result.StatusCV = self.currentPnl.comboStatus.GetValue()

        for unit in self.currentPnl.length_units:
            if unit.UnitsName == self.currentPnl.comboXUnits.GetValue():
                result.XLocationUnitsID = unit.UnitsID

            if unit.UnitsName == self.currentPnl.comboYUnits.GetValue():
                result.YLocationUnitsID = unit.UnitsID

            if unit.UnitsName == self.currentPnl.comboZUnits.GetValue():
                result.ZLocationUnitsID = unit.UnitsID

        for time in self.currentPnl.time_units:
            if time.UnitsName == self.currentPnl.comboIntendedUnits.GetValue():
                result.IntendedTimeSpacingUnitsID = time.UnitsID

        date = self.currentPnl.datePickerResult.GetValue()
        year = date.Year
        month = date.Month
        day = date.Day
        date = self.currentPnl.timeResult.GetWxDateTime()
        hour = date.Hour
        minute = date.Minute
        second = date.Second
        date = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        result.ResultDateTime = date

        result.XLocation = self.currentPnl.txtX.GetValue()
        result.YLocation = self.currentPnl.txtY.GetValue()
        result.ZLocation = self.currentPnl.txtZ.GetValue()

        result.IntendedTimeSpacing = self.currentPnl.txtIntended.GetValue()

        # self.database.getUpdateSession().updateResult(pass in result object)
        session = self.database.getUpdateSession()
        session.updateResult(result=result)

        self.returnValue = wx.ID_OK
        self.Close()

    def onPrev(self, event):
        self.currentPnl.Hide()
        self.currentPnl = self.pnlList[self.pnlList.index(self.currentPnl)-1]
        self.currentPnl.Show()
        self.Layout()
        self.mainSizer.Fit(self)
        
        if self.currentPnl == self.pnlList[0]:
            self.btnPrev.Enable(False)
        else:
            self.btnPrev.Enable(True)

        if self.currentPnl == self.pnlList[-1]:
            self.btnNext.SetLabel("Finish")
            self.btnNext.Unbind(wx.EVT_BUTTON)
            self.btnNext.Bind(wx.EVT_BUTTON, self.onFinish)
        else:
            self.btnNext.SetLabel("Next >")
            self.btnNext.Unbind(wx.EVT_BUTTON)
            self.btnNext.Bind(wx.EVT_BUTTON, self.onNext)

        event.Skip()

    def onNext(self, event):
        self.btnNext.Enable(False)
        self.currentPnl.Hide()
        self.currentPnl = self.pnlList[self.pnlList.index(self.currentPnl)+1]
        self.currentPnl.Show()
        self.Layout()
        self.mainSizer.Fit(self)

        if self.currentPnl == self.pnlList[0]:
            self.btnPrev.Enable(False)
        else:
            self.btnPrev.Enable(True)

        if self.currentPnl == self.pnlList[-1]:
            self.CenterOnParent()
            self.currentPnl.check_required_fields()
            self.btnNext.SetLabel("Finish")
            self.btnNext.Unbind(wx.EVT_BUTTON)
            self.btnNext.Bind(wx.EVT_BUTTON, self.onFinish)
        else:
            self.btnNext.SetLabel("Next >")
            self.btnNext.Unbind(wx.EVT_BUTTON)
            self.btnNext.Bind(wx.EVT_BUTTON, self.onNext)
            
        event.Skip()


if __name__ == '__main__': 
    app = wx.App(False) 
    wiz = WizardDialog(None) 
    wiz.addPage(SampFeatSelectPanel) 
    wiz.addPage(VariableSelectPanel) 
    wiz.addPage(UnitSelectPanel) 
    wiz.addPage(ProcLevelSelectPanel) 
    wiz.addPage(ActionsSelectPanel) 
    # wiz.addPage(ResultPageView)
    wiz.ShowModal() 
    app.MainLoop() 

