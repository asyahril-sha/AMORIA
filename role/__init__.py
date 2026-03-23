# role/__init__.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Role Behaviors Package
=============================================================================
"""

from .base import RoleBehavior
from .ipar import IparBehavior
from .pelakor import PelakorBehavior
from .istri_orang import IstriOrangBehavior
from .janda import JandaBehavior
from .pdkt import PDKTBehavior
from .sepupu import SepupuBehavior
from .teman_kantor import TemanKantorBehavior
from .teman_sma import TemanSmaBehavior
from .mantan import MantanBehavior

__all__ = [
    'RoleBehavior',
    'IparBehavior',
    'PelakorBehavior',
    'IstriOrangBehavior',
    'JandaBehavior',
    'PDKTBehavior',
    'SepupuBehavior',
    'TemanKantorBehavior',
    'TemanSmaBehavior',
    'MantanBehavior',
]
