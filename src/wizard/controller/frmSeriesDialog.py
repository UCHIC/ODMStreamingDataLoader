import wx
import sys
from src.wizard.view.clsSeriesSelectPanel import SeriesSelectPanelView
from src.wizard.view.clsCustomDialog import CustomDialog
from src.wizard.controller.WizardDialog import WizardDialog
from src.wizard.controller.frmSampFeatSelectPanel import SampFeatSelectPanel
from src.wizard.controller.frmVariableSelectPanel import VariableSelectPanel
from src.wizard.controller.frmUnitSelectPanel import UnitSelectPanel
from src.wizard.controller.frmProcLevelSelectPanel import ProcLevelSelectPanel
from src.wizard.controller.frmActionsSelectPanel import ActionsSelectPanel
from src.wizard.controller.frmResultSummaryPanel import ResultSummaryPanel
from src.wizard.models.ResultMapping import ResultMapping


class SeriesSelectDialog(CustomDialog):
    def __init__(self, parent, variable, database):
        super(SeriesSelectDialog, self).__init__(parent=parent, title="Select Result for %s" % variable, size=wx.Size(700, 500))
        self.database = database

        self.parent = parent
        self.read = database.getReadSession()

        self._auto_width_style = wx.LIST_AUTOSIZE
        if sys.platform == "win32":
            self._auto_width_style = wx.LIST_AUTOSIZE_USEHEADER

        self.existingResult = None
        #read.getDetailedResultInfo("Time series coverage")
        self.seriesSelectPanel = SeriesSelectPanelView(self)
        self.addPanel(self.seriesSelectPanel)
        self.seriesSelectPanel.okBtn.Disable()
        self.seriesSelectPanel.editBtn.Disable()

        self.seriesSelectPanel.newBtn.Bind(wx.EVT_BUTTON, self.onNew)
        self.seriesSelectPanel.editBtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.seriesSelectPanel.okBtn.Bind(wx.EVT_BUTTON, self.onOK)

        self.seriesSelectPanel.listCtrl.SetObjects(self.read.getDetailedResultInfo("Time series coverage"))
        self.auto_size_table()

        self.seriesSelectPanel.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_item)
        self.seriesSelectPanel.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_item)

        self.seriesSelectPanel.listCtrl.SetSingleStyle(style=wx.LC_SINGLE_SEL)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.seriesSelectPanel.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_keyboard_pressed_down)

    def on_keyboard_pressed_down(self, event):
        pass

    def on_close(self, event):
        self.Destroy()

    # ================== #
    # > Event Handlers < #
    # ================== #

    def auto_size_table(self):
        for i in range(self.seriesSelectPanel.listCtrl.GetColumnCount()):
            self.seriesSelectPanel.listCtrl.SetColumnWidth(col=i, width=self._auto_width_style)

    def on_deselect_item(self, event):
        self.seriesSelectPanel.okBtn.Disable()
        self.seriesSelectPanel.editBtn.Disable()

    def onNew(self, event):
        wiz = WizardDialog(self, database=self.database, title="New Result Wizard", result=None)
        
        wiz.addPage(SampFeatSelectPanel)
        wiz.addPage(VariableSelectPanel)
        wiz.addPage(UnitSelectPanel) 
        wiz.addPage(ProcLevelSelectPanel) 
        wiz.addPage(ActionsSelectPanel) 
        wiz.addPage(ResultSummaryPanel)

        wiz.CenterOnParent()
        if wiz.ShowModal() == wx.ID_OK:
            wiz.Center()
            read = self.database.getReadSession()

            r = read.getDetailedResultInfo("Time series coverage", 
                                            wiz.result.ResultID)
            r_id = r[0].ResultID ###DetailedResult instance has no attribute resultID

            r_id = r[0].ResultID
    
            detailedResults = read.getDetailedResultInfo("Time series coverage")
            self.seriesSelectPanel.listCtrl.SetObjects(detailedResults)

            for i in detailedResults:
                if i.ResultID == r_id:
                    self.seriesSelectPanel.listCtrl.SelectObject(\
                        i, deselectOthers=True,
                        ensureVisible=True)
        else:
            pass
            #wx.MessageBox('An error occurred while creating a new result', 'Error')
        
        event.Skip()

    def on_select_item(self, event):
        self.seriesSelectPanel.editBtn.Enable()
        self.seriesSelectPanel.okBtn.Enable()
        self.existingResult = self.seriesSelectPanel.listCtrl.GetSelectedObject()

    def Warning(parent, message, caption ='Warning!'):
        dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def onEdit(self, event):
        message = 'Warning, you may ruin the integrity of your data when using this feature'
        dlg = wx.MessageDialog(self, message=message, caption='Warning')
        dlg.SetOKCancelLabels(ok="Continue", cancel="Cancel")

        if dlg.ShowModal() == wx.ID_OK:
            result = self.read.getResults(ids=[self.existingResult.ResultID])
            result = result[0] if len(result) > 0 else None

            wiz = WizardDialog(self, database=self.database, title="Edit Result Wizard", result=result)
            wiz.centerSelf()
            wiz.addPage(SampFeatSelectPanel)
            wiz.addPage(VariableSelectPanel)
            wiz.addPage(UnitSelectPanel)
            wiz.addPage(ProcLevelSelectPanel)
            wiz.addPage(ActionsSelectPanel)
            wiz.addPage(ResultSummaryPanel)
            wiz.CenterOnParent()
            wiz.ShowModal()

        dlg.Destroy()

    def onOK(self, event):
        obj = self.seriesSelectPanel.listCtrl.GetSelectedObject()

        mapping = ResultMapping(obj.ResultID,
            obj.SamplingFeatureCode,
            obj.SamplingFeatureName,
            obj.MethodCode,
            obj.MethodName,
            obj.VariableCode,
            obj.VariableNameCV,
            obj.ProcessingLevelCode,
            obj.ProcessingLevelDefinition,
            obj.UnitsName)

        self.selectedResult = mapping

        event.Skip()
