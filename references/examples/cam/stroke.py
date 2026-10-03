"""Illustrative 30-unit lift: 180 rise, 30 dwell, 90 return, 60 dwell."""
import math

def stroke(theta_deg):
 if theta_deg<180:return 15*(1-math.cos(math.pi*theta_deg/180))
 if theta_deg<210:return 30.
 if theta_deg<300:return 15*(1+math.cos(math.pi*(theta_deg-210)/90))
 return 0.
