
import wx
import operator

class FileListView(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(FileListView, self).__init__(parent, **kwargs)

        supa_sizer = wx.FlexGridSizer(2, 1, 0, 0)
        supa_sizer.SetFlexibleDirection(wx.BOTH)
        supa_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        size = tuple(map(operator.sub, parent.GetSize(), (20, 150)))
        
        self.fileListCtrl = wx.ListCtrl(self, wx.ID_ANY,
                        wx.DefaultPosition, size,
                        wx.LC_HRULES | \
                        wx.LC_REPORT | wx.LC_VRULES)
       
        self.fileListCtrl.InsertColumn(0, 'ID')
        self.fileListCtrl.InsertColumn(1, 'Server')
        self.fileListCtrl.InsertColumn(2, 'Database')
        self.fileListCtrl.InsertColumn(3, 'Data File Location')
        self.fileListCtrl.InsertColumn(4, 'Period')
        self.fileListCtrl.InsertColumn(5, 'Scheduled Begin Time')
        self.fileListCtrl.InsertColumn(6, 'Last Update')
        supa_sizer.Add(self.fileListCtrl, 0, wx.ALL, 5)

        self.SetSizer(supa_sizer)
        self.Layout()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelection,
            self.fileListCtrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick,
            self.fileListCtrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselection,
            self.fileListCtrl)
    
    def onSelection(self, event):
        event.Skip()

    def onDoubleClick(self, event):
        event.Skip()

    def onDeselection(self, event):
        event.Skip()

    def __del__(self):
        pass

