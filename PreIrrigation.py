#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AquaCrop crop growth model

import numpy as np

from hydrology_funs import *

import logging
logger = logging.getLogger(__name__)

class PreIrrigation(object):
    """Class to represent pre-irrigation when in net irrigation 
    mode.
    """
    def __init__(self, PreIrrigation_variable):
        self.var = PreIrrigation_variable

    def initial(self):
        arr_zeros = np.zeros((self.var.nRotation, self.var.nLat, self.var.nLon))
        self.PreIrr = np.copy(arr_zeros)
        self.IrrNet = np.copy(arr_zeros)
        
    def dynamic(self):
        # Expand dz and dzsum to rotation, lat, lon
        arr_ones = np.ones((self.var.nRotation, self.var.nLat, self.var.nLon))[None,:,:,:]
        dz = (self.var.dz[:,None,None,None] * arr_ones)
        dzsum = (self.var.dzsum[:,None,None,None] * arr_ones)

        # Calculate pre-irrigation requirement
        rootdepth = np.maximum(self.var.Zmin, self.var.Zroot)
        rootdepth = np.round(rootdepth * 100) / 100
        thCrit = (self.var.th_wp_comp + ((self.var.NetIrrSMT / 100) * (self.var.th_fc_comp - self.var.th_wp_comp)))

        # Conditions for applying pre-irrigation
        cond1 = ((self.var.IrrMethod == 4) & (self.var.DAP == 1) & ((dzsum - dz) < rootdepth) & (self.var.th < thCrit))

        # Update pre-irrigation and root zone water content (mm)
        PreIrr_req = ((thCrit - self.var.th) * 1000 * dz)
        PreIrr_req[np.logical_not(cond1)] = 0
        self.var.PreIrr = np.sum(PreIrr_req, axis=0)
                
    def add_pre_irrigation(self):
        self.var.IrrNet += self.var.PreIrr