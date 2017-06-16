import wx._core
import wx.lib.scrolledpanel
import wx.lib.intctrl


class ColoredPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredStaticText(wx.StaticText):
    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)
        self.SetForegroundColour('#ffffff')


class ColoredToolbar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredButton(wx.Button):
    def __init__(self, *args, **kwargs):
        wx.Button.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColoredToggleButton(wx.ToggleButton):
    def __init__(self, *args, **kwargs):
        wx.ToggleButton.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColoredSlider(wx.Slider):
    def __init__(self, *args, **kwargs):
        wx.Slider.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredComboBox(wx.ComboBox):
    def __init__(self, *args, **kwargs):
        wx.ComboBox.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredCheckBox(wx.CheckBox):
    def __init__(self, *args, **kwargs):
        wx.CheckBox.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#2c3d51')
        self.SetForegroundColour('#ffffff')


class ColoredRadioButton(wx.RadioButton):
    def __init__(self, *args, **kwargs):
        wx.RadioButton.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#2c3d51')
        self.SetForegroundColour('#ffffff')


class ColoredTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#2c3d51')
        self.SetForegroundColour('#ffffff')


class ColoredScrolledPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#2c3d51')
        self.SetForegroundColour('#ffffff')


class ColoredDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredIntCtrl(wx.lib.intctrl.IntCtrl):
    def __init__(self, *args, **kwargs):
        wx.lib.intctrl.IntCtrl.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColoredStaticLine(wx.StaticLine):
    def __init__(self, *args, **kwargs):
        wx.StaticLine.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColoredFileDialog(wx.FileDialog):
    def __init__(self, *args, **kwargs):
        wx.FileDialog.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredMessageDialog(wx.MessageDialog):
    def __init__(self, *args, **kwargs):
        wx.MessageDialog.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredGauge(wx.Gauge):
    def __init__(self, *args, **kwargs):
        wx.Gauge.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColoredProgressDialog(wx.ProgressDialog):
    def __init__(self, *args, **kwargs):
        wx.ProgressDialog.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredColourDialog(wx.ColourDialog):
    def __init__(self, *args, **kwargs):
        wx.ColourDialog.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColouredSplitterWindow(wx.SplitterWindow):
    def __init__(self, *args, **kwargs):
        wx.SplitterWindow.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#356181')
        self.SetForegroundColour('#ffffff')


class ColouredFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')


class ColoredMenuBar(wx.MenuBar):
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        self.SetBackgroundColour('#263646')
        self.SetForegroundColour('#ffffff')

