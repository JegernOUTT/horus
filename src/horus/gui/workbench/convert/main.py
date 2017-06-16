import wx._core
import threading

import logging

from horus.gui.colored.colored_elements import ColoredProgressDialog, ColoredMessageDialog
from horus.util import resources, system
from horus.gui.engine import driver
from horus.gui.workbench.workbench import Workbench

logger = logging.getLogger(__name__)


class ConvertWorkbench(Workbench):
    def __init__(self, parent, toolbar_convert, scanning_workbench,
                 on_mesh_reconstruction_ended=None):
        Workbench.__init__(self, parent, name=_('Converting workbench'))
        self.toolbar_convert = toolbar_convert
        ToolbarConvert(parent, self.toolbar_convert, scanning_workbench,
                       on_mesh_reconstruction_ended)

    def on_open(self):
        pass

    def reset(self):
        pass

    def on_close(self):
        pass

    def setup_engine(self):
        pass

    def add_pages(self):
        pass

    def add_panels(self):
        pass


class ToolbarConvert:
    def __init__(self,
                 parent,
                 toolbar,
                 scanning_workbench,
                 on_mesh_reconstruction_ended):
        self.parent = parent
        self.toolbar = toolbar
        self.on_mesh_reconstruction_ended = on_mesh_reconstruction_ended
        self.scanning_workbench = scanning_workbench
        # Elements
        self.mesh_reconstruction_tool = self.toolbar.AddLabelTool(
            1, _("Mesh reconstruction"),
            wx.Bitmap(resources.get_path_for_image("mesh.png")), shortHelp=_("Mesh reconstruction"))
        self.toolbar.Realize()

        self._enable_tool(self.mesh_reconstruction_tool, True)

        self.reconstruction_thread = None
        self.reconstruction_thread_dialog = None
        self.canceled = False
        self.is_reconstructed = False
        self.normals_calculated = False

        # Events
        self.toolbar.Bind(wx.EVT_TOOL, self.on_mesh_reconstruction_clicked, self.mesh_reconstruction_tool)

    def __reconstruction(self):
        try:
            self.canceled = False
            self.scanning_workbench.scene_view._object._mesh.start_normals_with_normal_estimation()
            while not self.canceled:
                is_finished = self.scanning_workbench.scene_view._object. \
                    _mesh.is_finished_normals_with_normal_estimation()
                if is_finished:
                    self.normals_calculated = True
                    break

            if not self.canceled:
                self.scanning_workbench.scene_view._object._mesh.result_normals_with_normal_estimation()
                self.scanning_workbench.scene_view._object._mesh.start_reconstruct_poisson()

            while not self.canceled:
                is_finished = self.scanning_workbench.scene_view._object. \
                    _mesh.is_finished_reconstruct_poisson()
                if is_finished:
                    self.is_reconstructed = True
                    break

            if not self.canceled:
                output = self.scanning_workbench.scene_view._object._mesh.result_normals_reconstruct_poisson()
                wx.CallAfter(lambda: self.scanning_workbench.scene_view.load_file(output))
                wx.CallAfter(lambda: self.reconstruction_thread_dialog.Update(100))
                wx.CallAfter(lambda: self.on_mesh_reconstruction_ended(True))
                # wx.CallAfter(lambda: self.reconstruction_thread_dialog.Destroy())
            else:
                self.scanning_workbench.scene_view._object._mesh.stop_normals_with_normal_estimation()
                self.scanning_workbench.scene_view._object._mesh.stop_normals_reconstruct_poisson()
                self.scanning_workbench.scene_view._object._mesh.clear_normals()
                wx.CallAfter(lambda: self.reconstruction_thread_dialog.Resume())
                wx.CallAfter(lambda: self.reconstruction_thread_dialog.Update(100))
                wx.CallAfter(lambda: self.on_mesh_reconstruction_ended(True))
                # wx.CallAfter(lambda: self.reconstruction_thread_dialog.Destroy())
        except Exception as e:
            logger.error('Error while mesh construct: {}'.format(e))
            wx.CallAfter(lambda: self.reconstruction_thread_dialog.Update(100))
            wx.CallAfter(lambda: self.on_mesh_reconstruction_ended(False))
            wx.CallAfter(lambda: self.reconstruction_thread_dialog.Destroy())

    def on_mesh_reconstruction_clicked(self, event):
        if self.scanning_workbench.scene_view._object is not None:
            self.reconstruction_thread_dialog = ColoredProgressDialog(title="Waiting reconstruction",
                                                                      message="Please, wait mesh reconstruction",
                                                                      maximum=100,
                                                                      parent=self.parent,
                                                                      style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
                                                                            | wx.PD_CAN_ABORT | wx.PD_SMOOTH
                                                                            | wx.PD_ELAPSED_TIME)
            self.normals_calculated = False
            self.is_reconstructed = False
            self.reconstruction_thread = threading.Thread(target=self.__reconstruction)
            self.reconstruction_thread.start()
            self.reconstruction_thread_dialog.Update(50, 'Please, wait normal calculation')
            while not self.is_reconstructed:
                self.reconstruction_thread_dialog.Pulse('')
                threading._sleep(0.025)
                if self.normals_calculated and not self.reconstruction_thread_dialog.WasCancelled():
                    self.reconstruction_thread_dialog.Update(50, 'Please, wait mesh reconstruction')
                    self.normals_calculated = False
                if self.reconstruction_thread_dialog.WasCancelled():
                    self.canceled = True

            self.reconstruction_thread.join()
        else:
            self._show_message(_("ToolbarConvert"), wx.ICON_ERROR, _("Object is empty"))

    def _show_message(self, title, style, desc):
        dlg = ColoredMessageDialog(self.toolbar, desc, title, wx.OK | style)
        dlg.ShowModal()
        dlg.Destroy()

    def _enable_tool(self, item, enable):
        self.toolbar.EnableTool(item.GetId(), enable)
