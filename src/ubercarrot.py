import wx


__author__ = 'Callum McLean'


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="UberCarrot", size=(-1, -1))

        print "Loading UI..."
        sizer_window = wx.BoxSizer(wx.VERTICAL) # All the stuff goes in here.

        # We need lots of text fields, to enter text in!
        # These also need labels.
        # To keep thing simple, we'll group each text-field/label pair in a
        # mini-array, which will populate a large array of all of the text fields.
        # There's also a separate sizer for all of the text controls.

        num_text_fields = 20 # How many text fields do we want to provide?
        sizer_text_fields = wx.FlexGridSizer(num_text_fields, 2)
        self.textInputFields = []

        for i in xrange(0, num_text_fields):
            text_field = wx.TextCtrl(self)
            text_field_label = wx.StaticText(self, -1, "f{0} text".format(i))
            print "\tAdding text field: f{0}".format(i)
            controls = [text_field_label, text_field]
            self.textInputFields.append(controls)
            sizer_text_fields.AddMany(controls)

        print "\tAdding SUBMIT button" # The important one
        self.button_submit = wx.Button(self, -1, "SUBMIT", style=wx.BU_BOTTOM)

        # All together, now!
        sizer_window.Add(sizer_text_fields)
        sizer_window.Add(self.button_submit)
        self.SetSizerAndFit(sizer_window)

        # Boom.
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    window = MainWindow()
    app.MainLoop()
