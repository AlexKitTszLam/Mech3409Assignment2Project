# Assumes that we only look at the wheel example

#Libaries
import math

import sys
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader

#Equation Variables (stuff needed to calculate stuff)
ForceLow = None
ForceHigh = None

#mm
DiaShaft = None
RadWheel = None
LengthShaft = None

#mpa
Se = None
Sut = None
Sy = None

#calculated variables (stuff from calculations)
ForceMidrange = None
ForceAlternating = None

StressBendingMidrange = None
StressTorsionMidrange = None

StressBendingAlternating = None
StressTorsionAlternating = None

StressVonMisesAlternating = None
StressVonMisesMidrange = None

NfGoodman = None
NyGoodMan = None
NfGerber = None

MaxAxialLoad = None # Problem 4

#define equations for calcs

def FaCalc(ForceLow, ForceHigh):
     return abs((ForceHigh - ForceLow) / 2)

def FmCalc(ForceLow, ForceHigh):
    return (ForceHigh+ForceLow) / 2

def BendingCalc(InputForce, LengthShaft, DiaShaft):
    C = (DiaShaft / 2)
    I = (math.pi/64)*(DiaShaft**4)
    M = InputForce * LengthShaft

    return (M*C)/I

def TorsionCalc(InputForce, LengthShaft, DiaShaft, RadWheel):
    C = (DiaShaft / 2)
    J = (math.pi/32)*(DiaShaft**4)
    T = InputForce * RadWheel

    return (T*C)/J

def VonMisesCalc(Stress, Torsion): #This is a shortform of the actual vonmises formula. It works. (no axial loads, Kf = 1 due to round shaft)
    return math.sqrt((Stress**2) + (3*Torsion**2))

def NfGoodmanCalc(StressAlt, StressMid, Se, Sut):
    return 1 / ( (StressAlt / Se) + (StressMid / Sut) )

def NyGoodmanCalc(StressAlt, StressMid, Sy):
    return Sy / (StressMid + StressAlt)

def NyGerberCalc(StressAlt, StressMid, Se, Sut): # due to length of equation, this was convered through the use of ai.
    return 0.5 * ((Sut / StressMid) ** 2) * (StressAlt / Se) * (-1 + math.sqrt(1 + (((2 * StressMid * Se) / (Sut * StressAlt)) ** 2)))

def MaxAxialLoadCalc(StressBendingMid, StressTorsionMid, StressVMAlt, Se, Sut, DiaShaft):
    MaxStress = Sut * (1 - (StressVMAlt / Se))
    StressAxial = math.sqrt(MaxStress**2 - 3*(StressTorsionMid**2)) - StressBendingMid
    print(f"stress axial max = {StressAxial}")
    print(f"stress max = {MaxStress}")
    return StressAxial * ((math.pi / 4)*DiaShaft**2)


#gui code (runs the gui):
loader = QUiLoader()
app = QtWidgets.QApplication(sys.argv)
window = loader.load("Math.ui", None)

#def that calculates the values

def CalcNumbers():
    try:
        #grab values
        ForceLow = float(window.ForceMinInput.text())
        ForceHigh = float(window.ForceMaxInput.text())
        DiaShaft = float(window.DiaShaftInput.text())
        RadWheel = float(window.RadiusWheelInput.text())
        LengthShaft = float(window.LengthShaftInput.text())
        Se = float(window.SeInput.text())
        Sy = float(window.SyInput.text())
        Sut = float(window.SutInput.text())

        #the functions
        ForceMidrange = FmCalc(ForceLow, ForceHigh)
        ForceAlternating = FaCalc(ForceLow, ForceHigh)

        StressBendingMidrange = BendingCalc(ForceMidrange, LengthShaft, DiaShaft)
        StressBendingAlternating = BendingCalc(ForceAlternating, LengthShaft, DiaShaft)

        StressTorsionMidrange = TorsionCalc(ForceMidrange, LengthShaft, DiaShaft, RadWheel)
        StressTorsionAlternating = TorsionCalc(ForceAlternating, LengthShaft, DiaShaft, RadWheel)

        StressVonMisesAlternating = VonMisesCalc(StressBendingAlternating, StressTorsionAlternating)
        StressVonMisesMidrange = VonMisesCalc(StressBendingMidrange, StressTorsionMidrange)

        NfGoodman = NfGoodmanCalc(StressVonMisesAlternating, StressVonMisesMidrange, Se, Sut)
        NyGoodman = NyGoodmanCalc(StressVonMisesAlternating, StressVonMisesMidrange, Sy)
        NfGerber = NyGerberCalc(StressVonMisesAlternating, StressVonMisesMidrange, Se, Sut)

        MaxAxialLoad = MaxAxialLoadCalc(StressBendingMidrange,StressTorsionMidrange,StressVonMisesAlternating,Se,Sut,DiaShaft)

        #Display values to the gui
        window.ForceMidTxt.setText(f"{ForceMidrange:.3f}")
        window.ForceAltTxt.setText(f"{ForceAlternating:.3f}")

        window.BendMidTxt.setText(f"{StressBendingMidrange:.3f}")
        window.BendAltTxt.setText(f"{StressBendingAlternating:.3f}")

        window.TorsionMidTxt.setText(f"{StressTorsionMidrange:.3f}")
        window.TorsionAltTxt.setText(f"{StressTorsionAlternating:.3f}")

        window.VonMisesMidTxt.setText(f"{StressVonMisesMidrange:.3f}")
        window.VonMisesAltTxt.setText(f"{StressVonMisesAlternating:.3f}")

        window.NfGoodmanTxt.setText(f"{NfGoodman:.3f}")
        window.NyGoodmanTxt.setText(f"{NyGoodman:.3f}")
        window.NfGerberTxt.setText(f"{NfGerber:.3f}")
        window.MaxAxialLoadTxt.setText(f"{MaxAxialLoad:.3f}")

    except ValueError:
        QtWidgets.QMessageBox.warning(
            window,
            "Invalid Input",
            "Please make sure all 8 input boxes contain valid numbers.",
        )
    except ZeroDivisionError:
        QtWidgets.QMessageBox.warning(
            window,
            "Math Error",
            "Division by zero occurred (check that Diameter, Se, Sut, and Midrange"
            " Stress are non-zero).",
        )
    except Exception as e:
        QtWidgets.QMessageBox.warning(
            window,
            "Calculation Error",
            f"An error occurred (e.g., negative square root for Max Axial Load):\n{e}",
        )

window.Calculate.clicked.connect(CalcNumbers)

window.show()
sys.exit(app.exec())































