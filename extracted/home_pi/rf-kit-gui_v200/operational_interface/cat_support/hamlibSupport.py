from enum import Enum

from constants import CURRENT_GUI_FOLDER
from operational_interface.cat_support.hamlib40rc2RigSupport import Hamlib40rc2RigSupport
from operational_interface.cat_support.hamlib465RigSupport import Hamlib465RigSupport


class HamlibSupport(Enum):
    HAMLIB_4_0_RC2 = ('{}/hamlib/v4_0_rc2/lib'.format(CURRENT_GUI_FOLDER), Hamlib40rc2RigSupport)
    HAMLIB_4_6_5 = ('{}/hamlib/v4_6_5_bindings_backport/lib'.format(CURRENT_GUI_FOLDER), Hamlib465RigSupport)

    def __init__(self, ld_path, python_support):
        self.ldPath = ld_path
        self.pythonSupport = python_support

    @classmethod
    def for_rig(cls, rig_model):
        if rig_model in Hamlib465RigSupport.supported_rigs():
            return HamlibSupport.HAMLIB_4_6_5
        elif rig_model in Hamlib40rc2RigSupport.supported_rigs():
            return HamlibSupport.HAMLIB_4_0_RC2
        else:
            raise KeyError(f"Unsupported rig model: {rig_model}")