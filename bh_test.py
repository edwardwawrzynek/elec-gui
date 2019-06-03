import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from device_gui import DeviceGUI, ChannelGUI
from dev_gui_option import DevOptionGUIGroup, DevOptionGUI

import numpy as np
import xarray as xr
from astropy import units as u


class BhTestChannelRealScalarTime(ChannelGUI):
    def __init__(self, dev):
        super().__init__(self, dev)
        self.dev = dev
        self.setName('Real Scalar Channel in Time')

        self.addOption(DevOptionGUI(
            'Min Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Value', 'float', lambda x: x, default=1.0))
        # NOTE: Sample Depth should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Sample Depth', 'float', lambda x: x, default=20.0))
        self.addOption(DevOptionGUI(
            'Sampling Frequency [Hz]', 'float', lambda x: x, default=1.0))

    def collectData(self):
        samp_depth = int(self.options.getStateByLabel('Sample Depth'))
        fs = self.options.getStateByLabel('Sampling Frequency [Hz]')
        max_val = self.options.getStateByLabel('Max Value')
        min_val = self.options.getStateByLabel('Min Value')

        if samp_depth < 1:
            raise ValueError('Sample Depth must be at least 1')
        if fs <= 0:
            raise ValueError('Sampling Frequency must be greater than zero')
        if max_val < min_val:
            raise ValueError('Max Value must not be less than Min Value')

        data = np.random.rand(samp_depth) * (max_val-min_val) + min_val
        t = np.arange(0, samp_depth/fs, 1/fs)

        return xr.DataArray(data, dims=('t'), coords={'t': t}, attrs={'units':{'t':u.s, '':u.V}})

    def getXAxisDim(self):
        return 't'


class BhTestChannelRealScalarFreq(ChannelGUI):
    def __init__(self, dev):
        super().__init__(self, dev)
        self.dev = dev
        self.setName('Real Scalar Channel in Frequency')

        self.addOption(DevOptionGUI(
            'Min Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Value', 'float', lambda x: x, default=1.0))
        self.addOption(DevOptionGUI(
            'Start Frequency [Hz]', 'float', lambda x: x, default=1.0))
        self.addOption(DevOptionGUI(
            'Stop Frequency [Hz]', 'float', lambda x: x, default=100.0))
        # NOTE: Frequency Stpes should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Frequency Steps', 'float', lambda x: x, default=20))

    def collectData(self):
        max_val = self.options.getStateByLabel('Max Value')
        min_val = self.options.getStateByLabel('Min Value')
        fstart = self.options.getStateByLabel('Start Frequency [Hz]')
        fstop = self.options.getStateByLabel('Stop Frequency [Hz]')
        steps = int(self.options.getStateByLabel('Frequency Steps'))

        if max_val < min_val:
            raise ValueError('Max Value must not be less than Min Value')
        if fstart < 0 or fstop < 0:
            raise ValueError('Negative Frequencies not allowed')
        if fstart > fstop:
            raise ValueError('Start Frequency may not exceed Stop Frequency')
        if fstart == fstop:
            raise NotImplementedError()
        if steps < 2:
            raise ValueError('Not enough frequency steps')

        data = np.random.rand(steps) * (max_val-min_val) + min_val
        f = np.linspace(fstart, fstop, steps)

        return xr.DataArray(data, dims=('f'), coords={'f': f}, attrs={'units':{'f':u.Hz, '':u.V}})

    def getXAxisDim(self):
        return 'f'


class BhTestChannelComplexScalarTime(ChannelGUI):

    def __init__(self, dev):
        super().__init__(self, dev)
        self.dev = dev
        self.setName('Complex Scalar Channel in Time')

        self.addOption(DevOptionGUI(
            'Min Real Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Real Value', 'float', lambda x: x, default=1.0))
        self.addOption(DevOptionGUI(
            'Min Imag Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Imag Value', 'float', lambda x: x, default=1.0))
        # NOTE: Sample Depth should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Sample Depth', 'float', lambda x: x, default=20.0))
        self.addOption(DevOptionGUI(
            'Sampling Frequency [Hz]', 'float', lambda x: x, default=1.0))

    def collectData(self):
        samp_depth = int(self.options.getStateByLabel('Sample Depth'))
        fs = self.options.getStateByLabel('Sampling Frequency [Hz]')
        max_r = self.options.getStateByLabel('Max Real Value')
        min_r = self.options.getStateByLabel('Min Real Value')
        max_i = self.options.getStateByLabel('Max Imag Value')
        min_i = self.options.getStateByLabel('Min Imag Value')

        if samp_depth < 1:
            raise ValueError('Sample Depth must be at least 1')
        if fs <= 0:
            raise ValueError('Sampling Frequency must be greater than zero')
        if max_r < min_r:
            raise ValueError(
                'Max Real Value must not be less than Min Real Value')
        if max_i < min_i:
            raise ValueError(
                'Max Imag Value must not be less than Min Imag Value')

        data_r = np.random.rand(samp_depth) * (max_r-min_r) + min_r
        data_i = np.random.rand(samp_depth) * (max_i-min_i) + min_i
        data = data_r + data_i * 1j
        t = np.arange(0, samp_depth/fs, 1/fs)

        return xr.DataArray(data, dims=('t'), coords={'t': t})

    def getXAxisDim(self):
        pass


class BhTestChannelRealArrayTime(ChannelGUI):

    def __init__(self, dev):
        super().__init__(self, dev)
        self.dev = dev
        self.setName('Real Array Channel in Time')

        self.addOption(DevOptionGUI(
            'Min Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Value', 'float', lambda x: x, default=1.0))
        # NOTE: Rows should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Rows', 'float', lambda x: x, default=1.0))
        # NOTE: Columns should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Columns', 'float', lambda x: x, default=1.0))
        # NOTE: Sample Depth should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Sample Depth', 'float', lambda x: x, default=20.0))
        self.addOption(DevOptionGUI(
            'Sampling Frequency [Hz]', 'float', lambda x: x, default=1.0))

    def collectData(self):
        samp_depth = int(self.options.getStateByLabel('Sample Depth'))
        fs = self.options.getStateByLabel('Sampling Frequency [Hz]')
        max_val = self.options.getStateByLabel('Max Value')
        min_val = self.options.getStateByLabel('Min Value')
        rows = int(self.options.getStateByLabel('Rows'))
        cols = int(self.options.getStateByLabel('Columns'))

        if samp_depth < 1:
            raise ValueError('Sample Depth must be at least 1')
        if fs <= 0:
            raise ValueError('Sampling Frequency must be greater than zero')
        if max_val < min_val:
            raise ValueError('Max Value must not be less than Min Value')
        if rows < 1:
            raise ValueError('Rows must be at least 1')
        if cols < 1:
            raise ValueError('Columns must be at least 1')

        data = np.random.rand(samp_depth, rows, cols) * \
            (max_val-min_val) + min_val
        t = np.arange(0, samp_depth/fs, 1/fs)

        # NOTE: 'row' and 'col' are dimensions without coordinates. This is allowed but they should also be allowed to have coordinates
        return xr.DataArray(data, dims=('t', 'row', 'col'), coords={'t': t}, attrs={'units':{'': u.V, 't':u.s, 'row':u.dimensionless_unscaled, 'col':u.dimensionless_unscaled}})

    def getAdditionalDims(self):
        return ['row', 'col']

    def getXAxisDim(self):
        return 't'


class BhTestChannelRealScalarTimeUnits(ChannelGUI):
    def __init__(self, dev):
        super().__init__(self, dev)
        self.dev = dev
        self.setName('Real Scalar Channel in Time with Units')

        self.addOption(DevOptionGUI(
            'Min Value', 'float', lambda x: x, default=-1.0))
        self.addOption(DevOptionGUI(
            'Max Value', 'float', lambda x: x, default=1.0))
        # NOTE: Sample Depth should actually be an integer but taking int(value) later works
        self.addOption(DevOptionGUI(
            'Sample Depth', 'float', lambda x: x, default=20.0))
        self.addOption(DevOptionGUI(
            'Sampling Frequency [Hz]', 'float', lambda x: x, default=1.0))
        self.addOption(DevOptionGUI(
            'Horizontal Unit', 'string', lambda x: x, default='s'
        ))
        self.addOption(DevOptionGUI(
            'Vertical Unit', 'string', lambda x: x, default='V'
        ))

    def collectData(self):
        samp_depth = int(self.options.getStateByLabel('Sample Depth'))
        fs = self.options.getStateByLabel('Sampling Frequency [Hz]')
        max_val = self.options.getStateByLabel('Max Value')
        min_val = self.options.getStateByLabel('Min Value')
        vert_unit = self.options.getStateByLabel('Vertical Unit')
        horiz_unit = self.options.getStateByLabel('Horizontal Unit')

        if samp_depth < 1:
            raise ValueError('Sample Depth must be at least 1')
        if fs <= 0:
            raise ValueError('Sampling Frequency must be greater than zero')
        if max_val < min_val:
            raise ValueError('Max Value must not be less than Min Value')
        try:
            u.Unit(vert_unit)
        except ValueError:
            raise ValueError(f'{vert_unit} is not a valid unit')
        try:
            u.Unit(horiz_unit).to(u.s)
        except ValueError:
            raise ValueError(f'{horiz_unit} is not a valid unit of time')

        data = np.random.rand(samp_depth) * (max_val-min_val) + min_val
        t = (np.arange(0, samp_depth/fs, 1/fs)
             * u.s).to(u.Unit(horiz_unit))

        return xr.DataArray(
            data,
            dims=('t'),
            coords={'t': t},
            attrs={'units': {'': u.Unit(vert_unit), 't': u.Unit(horiz_unit)}}
        )

    def getXAxisDim(self):
        return 't'


class BhTestDevice(DeviceGUI):

    def __init__(self):
        super().__init__(None)
        self.setName('BH Test Device')
        chan_types = (
            BhTestChannelRealScalarTime,
            BhTestChannelRealScalarFreq,
            BhTestChannelComplexScalarTime,
            BhTestChannelRealArrayTime,
            BhTestChannelRealScalarTimeUnits,
        )
        for chan_type in chan_types:
            self.addChannel(chan_type(self))