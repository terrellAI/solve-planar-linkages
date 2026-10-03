"""Confirmed teaching example: r0=40 mm, lift=20 mm, phases 60/20/40/240 deg."""
import math

def stroke(theta_deg):
 if not 0<=theta_deg<=360:raise ValueError('angle outside [0,360]')
 if theta_deg<60:return 10*(1-math.cos(math.pi*theta_deg/60))
 if theta_deg<80:return 20.
 if theta_deg<120:return 10*(1+math.cos(math.pi*(theta_deg-80)/40))
 return 0.
