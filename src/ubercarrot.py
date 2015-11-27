import wx
import wx.lib.agw.aui as aui


__author__ = 'Callum McLean'


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="UberCarrot", size=(-1, -1))

        self._mgr = aui.AuiManager()

        # notify AUI which frame to use
        self._mgr.SetManagedWindow(self)

        print "Loading UI..."
        # To avoid having the ugly dark-grey background on Windows, we'll use a wxPanel as the only child object
        # of the wxFrame. All the control will be children of the wxPanel.

        self.panel_text_boxes = wx.Panel(self, -1)
        sizer_data_entry = wx.BoxSizer(wx.VERTICAL) # All the text-stuff and the submit button goes in here.
        self.panel_cg_recall = wx.Panel(self, -1)
        sizer_cg_recall = wx.BoxSizer(wx.VERTICAL) # We'll put all the 'Recall Template' buttons in here

        # We need lots of text fields, to enter text in!
        # These also need labels.
        # To keep thing simple, we'll group each text-field/label pair in a
        # mini-array, which will populate a large array of all of the text fields.
        # There's also a separate sizer for all of the text controls.

        num_text_fields = 20 # How many text fields do we want to provide?
        sizer_text_fields = wx.FlexGridSizer(num_text_fields, 2)
        self.textInputFields = []

        for i in xrange(0, num_text_fields):
            text_field = wx.TextCtrl(self.panel_text_boxes)
            text_field_label = wx.StaticText(self.panel_text_boxes, -1, "f{0} text".format(i))
            print "\tAdding text field: f{0}".format(i)
            controls = [text_field_label, text_field]
            self.textInputFields.append(controls)
            sizer_text_fields.AddMany(controls)

        print "\tAdding SUBMIT button" # The important one
        self.button_submit = wx.Button(self.panel_text_boxes, -1, "SUBMIT", style=wx.BU_EXACTFIT)

        ################################
        # RECALL BUTTONS
        ################################

        num_templates = 5 # How many templates shall we have?
        self.template_buttons = []
        for i in xrange(0, num_templates):
            print "\tAdding recall button: #{0}".format(i)
            btn = wx.Button(self.panel_cg_recall, label="Recall Template {0}".format(i))
            self.template_buttons.append(btn)
            sizer_cg_recall.Add(btn)

        ################################
        # BUILD UI
        ################################

        # All together, now!
        sizer_data_entry.Add(sizer_text_fields)
        sizer_data_entry.Add(self.button_submit)
        self.panel_text_boxes.SetSizerAndFit(sizer_data_entry)

        self.panel_cg_recall.SetSizerAndFit(sizer_cg_recall)

        self._mgr.AddPane(self.panel_text_boxes, aui.AuiPaneInfo().Left().Caption("Pane Number One"))
        self._mgr.AddPane(self.panel_cg_recall, aui.AuiPaneInfo().Right().Caption("Pane Number Two"))

        self._mgr.Update()
        # Boom.
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    window = MainWindow()
    app.MainLoop()
