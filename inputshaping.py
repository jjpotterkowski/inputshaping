#-------------------------------------------------------------------------------
# Name:        inputshaping
# Purpose:     Allow user to generate basic input shapers in continuous and
#              digital forms.  Some functions based on code by Dr. Joshua
#              Vaughan and C.J. Adams from Georgia Institute of Technology.
#              Digitization function based on code by C.J. Adams, implementing
#              techniques from Murphy, B.R. and Watanabe, I., "Digital Shaping
#              Filters for Reducing Machine Vibration," IEEE Transactions on
#              Robotics and Automation, Vol. 8, No. 2, April 1992.
#
# Author:      James Jackson Potter
# Email:       jjpotterkowski@gmail.com
#
# Created:     28/01/2014 (dd/mm/yyyy)
# Copyright:   (c) 2014 James Jackson Potter
# License:     This program is free software; you can redistribute it and/or
#              modify it under the terms of the GNU General Public License
#              as published by the Free Software Foundation; either version 2
#              of the License, or (at your option) any later version.
#
#              This program is distributed in the hope that it will be useful,
#              but WITHOUT ANY WARRANTY; without even the implied warranty of
#              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#              GNU General Public License for more details.
#
#              You should have received a copy of the GNU General Public License
#              along with this program; if not, write to the Free Software
#              Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#              02110-1301, USA.
#-------------------------------------------------------------------------------
from __future__ import print_function
import matplotlib.pyplot as mpl
import numpy as np

__version__ = "1.0"


class InputShaper:
    """
    To construct input shaper "yourShaperObject" to suppress a mode with
    wn = 1 rad/s, zeta = 0.1, sampling at fps = 100, enter:
    >>> myShaperObject = InputShaper(1, 0.1, 100)

    The input shaper will be initialized as unshaped (shaperType = 'OFF').  To
    design a specific shaper, call one of the shaper type methods.  For example,
    enter the following for a ZV shaper:
    >>> myShaperObject.ZV()

    Most of the input shapers allow you to enter a "strength" for the input
    shaper, between 0 (unshaped) and 1 (unmodified input shaper).  For a ZVD
    shaper that only suppresses 50% of the vibration at the modeled frequency,
    but modifies the shaped command less than the original input shaper, enter:
    >>> myShaperObject.ZVD(0.5)

    NOTE: The UMZV and UMZVD input shapers are generated using polynomials in
    damping ratio zeta, and they may not be effective for damping ratios greater
    than zeta = 0.3.  They are also limited to amplitude values of -1 and 1, so
    adjusting the shaper strength of UMZV and UMZVD shapers is not an option.
    """


    def __init__(self, wn="natural frequency (rad/s)", zeta="damping ratio", fps="sampling rate (frame/sec)"):
        self.wn = wn
        self.zeta = zeta
        self.fps = fps
        self.dt = 1.0/fps
        self.wd = wn*np.sqrt((1.0 - zeta**2.0))
        self.Tn = (2.0*np.pi)/self.wn
        self.OFF()


    def __call__(self):
        self.display()


    def show(self):
        self.display()


    def display(self):
        print("")
        print("--INPUT SHAPER ATTRIBUTES--")
        print("Natural Frequency (rad/s):", self.wn)
        print("Damping Ratio:", self.zeta)
        print("Sampling Rate (frames/s):", self.fps)
        print("Input Shaper Type:", self.shaperType)
        print("Input Shaper Strength ([0, 1]):", self.strengthFrac)
        print("")
        print("--CONTINUOUS INPUT SHAPER--")
        print("Impulse Amplitudes:", self.conAmps)
        print("Impulse Times (s):", self.conTimes)
        print("")
        print("--DIGITAL INPUT SHAPER--")
        print("Impulse Amplitudes:", self.digAmps)
        print("Impulse Times (s):", self.digTimes)
        print("Impulse Steps:", self.digFrames)
        print("")


    def OFF(self):
        self.shaperType = "OFF"
        self.strengthFrac = np.nan
        self.conNum = 1
        self.conAmps = [1.0]
        self.conTimes = [0.0]
        self.digNum = 1
        self.digAmps = [1.0]
        self.digTimes = [0.0]
        self.digFrames = [0]


    def CUSTOM(self, impulseSeq=[0.5, 0.5, 0.0, 1.0]):
        self.shaperType = "CUSTOM"
        self.strengthFrac = np.nan
        assert np.size(impulseSeq)%2 == 0, "Custom impulse sequence must have an even number of elements!"
        self.conNum = np.size(impulseSeq)/2
        self.conAmps = impulseSeq[:self.conNum]
        self.conTimes = impulseSeq[self.conNum:]
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def ZV(self, strengthFrac=1):
        self.shaperType = "ZV"
        self.strengthFrac = strengthFrac
        self.conNum = 2
        self.conAmps = [0.5, 0.5]
        self.conTimes = [0, 0.5*self.Tn]
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def ZVD(self, strengthFrac=1):
        self.shaperType = "ZVD"
        self.strengthFrac = strengthFrac
        self.conNum = 3
        self.conAmps = [0.25, 0.5, 0.25]
        self.conTimes = [0, 0.5*self.Tn, self.Tn]
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def ZVDD(self, strengthFrac=1):
        self.shaperType = "ZVDD"
        self.strengthFrac = strengthFrac
        self.conNum = 4
        self.conAmps = [0.125, 0.375, 0.375, 0.125]
        self.conTimes = [0, 0.5*self.Tn, self.Tn, 1.5*self.Tn]
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def ZVDDD(self, strengthFrac=1):
        self.shaperType = "ZVDDD"
        self.strengthFrac = strengthFrac
        self.conNum = 5
        self.conAmps = [0.0625, 0.25, 0.375, 0.25, 0.0625]
        self.conTimes = [0, 0.5*self.Tn, self.Tn, 1.5*self.Tn, 2.0*self.Tn]
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def SNA(self, negativeAmp=0.5, strengthFrac=1):
        assert negativeAmp >= 0 and negativeAmp <= 1, "Negative impulse amplitude must be between 0 and 1!"
        self.shaperType = "SNA"
        self.strengthFrac = strengthFrac
        b = -1.0*negativeAmp
        a = (1.0 - b)/2
        self.conNum = 3
        self.conAmps = [a, b, a]
        self.conTimes = [0, (1/self.wn)*np.arccos(-b/(2*a)), (1/self.wn)*np.arccos(b**2/(2.0*a**2) - 1)]
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def EI(self, tolerableVib=0.05, strengthFrac=1):
        assert tolerableVib >= 0 and tolerableVib <= 1, "Tolerable vibration must be between 0 and 1!"
        self.shaperType = "EI"
        self.strengthFrac = strengthFrac
        self.conNum = 3
        self.conAmps = [0.25*(1+tolerableVib), 0.5*(1-tolerableVib), 0.25*(1+tolerableVib)]
        self.conTimes = [0, 0.5*self.Tn, self.Tn]
        self._relax_vibration(max([0, strengthFrac-tolerableVib]))
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def RM(self, impulseNum=3, strengthFrac=1):
        self.shaperType = "RM%i" %impulseNum
        self.strengthFrac = strengthFrac
        self.conNum = impulseNum
        (self.conAmps, self.conTimes) = self._generate_rm_impulses(impulseNum)
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def RM3(self, strengthFrac=1):
        impulseNum = 3
        self.shaperType = "RM3"
        self.strengthFrac = strengthFrac
        self.conNum = impulseNum
        (self.conAmps, self.conTimes) = self._generate_rm_impulses(impulseNum)
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def RM4(self, strengthFrac=1):
        impulseNum = 4
        self.shaperType = "RM4"
        self.strengthFrac = strengthFrac
        self.conNum = impulseNum
        (self.conAmps, self.conTimes) = self._generate_rm_impulses(impulseNum)
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def RM5(self, strengthFrac=1):
        impulseNum = 5
        self.shaperType = "RM5"
        self.strengthFrac = strengthFrac
        self.conNum = impulseNum
        (self.conAmps, self.conTimes) = self._generate_rm_impulses(impulseNum)
        self._relax_vibration(strengthFrac)
        self._scale_for_damping()
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def UMZV(self):
        """
        Partial input shaping is not available for the UMZV input shaper because
        impulse amplitudes must be 1, -1, and 1.  For partially-shaped versions
        of UMZV shaper (that technically do not fit into the category of UMZV),
        use SNA() method with negativeAmp=1.
        """
        self.shaperType = "UMZV"
        self.strengthFrac = 1
        t2 = scaled_cubic(0.16724, 0.27242, 0.20345, 0, self.zeta, self.Tn)
        t3 = scaled_cubic(0.33323, 0.00533, 0.17914, 0.20125, self.zeta, self.Tn)
        self.conNum = 3
        self.conAmps = [1, -1, 1]
        self.conTimes = [0, t2, t3]
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)


    def UMZVD(self):
        """
        Partial input shaping is not available for the UMZVD input shaper because
        impulse amplitudes must be 1, -1, 1, -1, and 1.
        """
        self.shaperType = "UMZVD"
        self.strengthFrac = 1
        t2 = scaled_cubic(0.08945, 0.28411, 0.23013, 0.16401, self.zeta, self.Tn)
        t3 = scaled_cubic(0.36613, -0.08833, 0.24048, 0.17001, self.zeta, self.Tn)
        t4 = scaled_cubic(0.64277, 0.29103, 0.23262, 0.43784, self.zeta, self.Tn)
        t5 = scaled_cubic(0.73228, 0.00992, 0.49385, 0.38633, self.zeta, self.Tn)
        self.conNum = 5
        self.conAmps = [1, -1, 1, -1, 1]
        self.conTimes = [0, t2, t3, t4, t5]
        (self.digNum, self.digAmps, self.digTimes, self.digFrames) = digitize_shaper(self.conAmps, self.conTimes, self.wn, self.zeta, self.dt)

    
    def off(self): self.OFF() # allow lower-case aliases for all shaper types
    def custom(self, impulseSeq=[0.5, 0.5, 0.0, 1.0]): self.CUSTOM(impulseSeq)
    def zv(self, strengthFrac=1): self.ZV(strengthFrac)
    def zvd(self, strengthFrac=1): self.ZVD(strengthFrac)
    def zvdd(self, strengthFrac=1): self.ZVDD(strengthFrac)
    def zvddd(self, strengthFrac=1): self.ZVDDD(strengthFrac)
    def sna(self, negativeAmp=0.5, strengthFrac=1): self.SNA(negativeAmp, strengthFrac)
    def ei(self, tolerableVib=0.05, strengthFrac=1): self.EI(tolerableVib, strengthFrac)
    def rm(self, impulseNum=3, strengthFrac=1): self.RM(impulseNum, strengthFrac)
    def rm3(self, strengthFrac=1): self.RM3(strengthFrac)
    def rm4(self, strengthFrac=1): self.RM4(strengthFrac)
    def rm5(self, strengthFrac=1): self.RM5(strengthFrac)
    def umzv(self): self.UMZV()
    def umzvd(self): self.UMZVD()
   

    def _generate_rm_impulses(self, impulseNum):
        impAmps = []
        impTimes = []
        for k in range(0, impulseNum):
            impAmps.append(((-1)**(k+1))*(1.0/(impulseNum-1.0)))
            impTimes.append(0.5*k*self.Tn)
        impAmps[0] = 0.5*impAmps[0] + 1
        impAmps[-1] = 0.5*impAmps[-1]
        return (impAmps, impTimes)


    def _relax_vibration(self, strengthFrac="Strength of input shaper, ranging from 0 (unshaped) to 1 (original input shaper)"):
        assert strengthFrac >= 0 and strengthFrac <= 1, "Strength fraction must be between 0 and 1!"
        partialFrac = 1 - strengthFrac

        if partialFrac == 0:
            pass
        elif partialFrac == 1:
            self.OFF()
        else:
            vibrationTolerance = 0.0001;
            iterationNum = 0;
            lowerBoundAdded = 0;
            upperBoundAdded = 1000.0;

            highValueVibration = residual_vibration(list(self.conAmps), list(self.conTimes), self.wn, 0, upperBoundAdded)
            assert highValueVibration > strengthFrac, "Must use a larger starting value of upperBoundAdded!"

            midValueAdded = (upperBoundAdded - lowerBoundAdded)/2 + lowerBoundAdded
            midValueVibration = residual_vibration(list(self.conAmps), list(self.conTimes), self.wn, 0, midValueAdded)

            while np.abs(midValueVibration - partialFrac) > vibrationTolerance:
                iterationNum = iterationNum + 1
                if midValueVibration > partialFrac:
                    upperBoundAdded = midValueAdded
                else:
                    lowerBoundAdded = midValueAdded
                midValueAdded = (upperBoundAdded - lowerBoundAdded)/2 + lowerBoundAdded
                midValueVibration = residual_vibration(list(self.conAmps), list(self.conTimes), self.wn, 0, midValueAdded)

            self.conAmps[0] = self.conAmps[0] + midValueAdded
            self.conAmps = [k/sum(self.conAmps) for k in self.conAmps]


    def _scale_for_damping(self):
        self.conTimes = [k/np.sqrt(1-self.zeta**2) for k in self.conTimes]
        self.conAmps = [self.conAmps[k]*np.e**(-self.zeta*self.wn*self.conTimes[k]) for k in range(0, self.conNum)]
        self.conAmps = [k/sum(self.conAmps) for k in self.conAmps]


    def sensitivity_curve(self, xLimits=[0.5, 1.5], wnNormalized=False):
        """
        Shows the level of residual vibration allowed by the input shaper as a
        function of frequency.  If optional input wnNormalized is set to "True",
        frequency values on x-axis will be divided by the input shaper's modeled
        natural frequency, wn.
        """
        wVec = np.linspace(xLimits[0], self.wn*xLimits[1], 3001)
        vibVec = []
        for w in wVec:
            vibVal = residual_vibration(self.conAmps, self.conTimes, w, self.zeta)
            vibVec.append(vibVal)
        if wnNormalized:
            wVec = [k/self.wn for k in wVec]
        mpl.plot(wVec, vibVec, linewidth=2)
        mpl.xlim([wVec[0], wVec[-1]])
        mpl.ylim([0, 1])
        if wnNormalized:
            mpl.xlabel("Normalized Frequency")
        else:
            mpl.xlabel("Frequency (rad/s)")
        mpl.ylabel("Normalized Vibration")
        mpl.show()


def digitize_shaper(amps, times, wn, zeta, dt):
    nAmps = len(amps)
    wd = wn*np.sqrt((1.0 - zeta**2.0))
    B = [amps[0]]
    t = [times[0]]
    if nAmps == 1:
        pass
    else:
        for i in range(1, nAmps):
            if times[i]%dt == 0:
                B.append(amps[i])
                t.append(times[i])
            else:
                tk = np.floor(times[i]/dt)*dt
                tkNext = np.ceil(times[i]/dt)*dt
                t.extend((tk, tkNext))
                phik = np.abs(tk - times[i])*wd
                phikNext = np.abs(tkNext - times[i])*wd
                Bk = amps[i]*np.e**(-zeta*(tk-times[i])*wn)*(np.sin(phikNext)/(np.sin(phikNext)*np.cos(phik) + np.sin(phik)*np.cos(phikNext)))
                BkNext = amps[i]*np.e**(-zeta*(tkNext-times[i])*wn)*(np.sin(phik)/(np.sin(phikNext)*np.cos(phik) + np.sin(phik)*np.cos(phikNext)))
                B.extend((Bk, BkNext))
    digNum = len(B)
    digAmps = [k/sum(B) for k in B]
    digTimes = t
    digFrames = [int(np.round(k/dt, 0)) for k in t]
    return (digNum, digAmps, digTimes, digFrames)


def residual_vibration(amps, times, wn, zeta, valueAdded=0):
    amps[0] = amps[0] + valueAdded
    amps = [k/sum(amps) for k in amps]

    nAmps = len(amps)
    wd = wn*np.sqrt(1.0 - zeta**2.0)
    C = []
    S = []
    for k in range(0, nAmps):
        C.append(amps[k]*np.e**(zeta*wn*times[k])*np.cos(wd*times[k]))
        S.append(amps[k]*np.e**(zeta*wn*times[k])*np.sin(wd*times[k]))
    resVib = np.e**(-zeta*wn*times[nAmps-1])*np.sqrt(sum(C)**2 + sum(S)**2)
    return resVib


def scaled_cubic(a0, a1, a2, a3, xIn, kIn):
    return kIn*(a0 + a1*xIn + a2*xIn**2 + a3*xIn**3)


def shapermaker():
    try:
        import shapermaker
    except ImportError:
        print("Could not import 'shapermaker' module!")
    guiInstance = shapermaker.run_gui()


def gui():
    shapermaker()
