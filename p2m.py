#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 00:48:54 2022

@author: clint
"""

#formal XYK implementation with xy = k = l^2 liquidity pool.
#follows the Runtime Verification xy=k paper

#import some stuff
import numpy as np
import random as rd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

#define action functions
def addLiquidity(delta_e,e,t,l):
    alpha = delta_e/e
    add_liq = 1+alpha
    e_new = add_liq*e
    t_new = add_liq*t
    l_new = add_liq*l
    return e_new, t_new, l_new

def removeLiquidity(delta_l,e,t,l):
    alpha = delta_l/l
    rem_liq = 1-alpha
    e_new = rem_liq*e
    t_new = rem_liq*t
    l_new = rem_liq*l
    return e_new, t_new, l_new

def getInputPrice(delta_x,x,y):
    #trader is selling dx and buying dy
    fee   = 0.003
    alpha = delta_x/x
    gamma = 1-fee
    delta_y = alpha*gamma/(1+alpha*gamma)*y
    return delta_y

def getOutputPrice(delta_y,x,y):
    #trader is buying dy and must spend dx
    fee  = 0.003
    beta = delta_y/y
    gamma = 1-fee
    delta_x = beta/(1-beta)/gamma*x 
    return delta_x

def ethToToken(delta_e,e,t):
    e_new = e + delta_e
    t_new = t - getInputPrice(delta_e,e,t)
    return e_new, t_new
    
def ethToToken2(delta_t,e,t): #ethToTokenExact in formalXYK paper
    t_new = t - delta_t
    e_new = e + getOutputPrice(delta_t,e,t)
    return e_new, t_new 

def tokenToEth(delta_t,e,t):
    t_new = t + delta_t
    e_new = e - getInputPrice(delta_t,t,e)
    return e_new, t_new   

def tokenToEth2(delta_e,e,t): #tokenToEthExact in formalXYK paper
    e_new = e - delta_e
    t_new = t + getOutputPrice(delta_e,t,e)
    return e_new, t_new 

def arbMToP_e(xp,yp,xm,ym):
    feeP = 0.003
    feeM = 0.002
    phiP = 1-feeP
    phiM = 1-feeM
    kp = xp*yp
    km = xm*ym
    
    #determine optimal arbitrage trade
    a = xp*ym - phiP*km + phiP*xm*ym
    b = xp*phiM + phiP*xm*phiM
    a0 = b**2
    b0 = 2*a*b + kp*phiM*b - b*kp*phiM
    c0 = a**2 + kp*phiM*a - b*kp*ym
    
    optimal_dym1 = (-b0 + np.sqrt(b0**2 - 4*a0*c0))/(2*a0)
    optimal_dym2 = (-b0 - np.sqrt(b0**2 - 4*a0*c0))/(2*a0)

    if optimal_dym1 >= 0:
        dym = optimal_dym1
    elif optimal_dym2 >= 0:
        dym = optimal_dym2
    else:
        dym = 0
    
    xm0 = xm
    #sell dym to market for dx and update state
    [xm,ym] = tokenToEth(dym,xm,ym)
    #sell dx = -(xmn1-xmn) to pool, receive dy, and  update pool state
    [xp, yp] = ethToToken(-(xm-xm0),xp,yp)
    
    return xp,yp,xm,ym


#number of simulation timesteps
numTimeSteps = 100
steps = list(range(0, numTimeSteps))
myRanChoice = [1,2,3,4]

#placeholder arrays
e = np.zeros(numTimeSteps)
t = np.zeros(numTimeSteps)
l = np.zeros(numTimeSteps)
k = np.zeros(numTimeSteps)
em = np.zeros(numTimeSteps)
tm = np.zeros(numTimeSteps)
lm = np.zeros(numTimeSteps)
km = np.zeros(numTimeSteps)

#initial states
e[0] = 1
t[0] = 1000
l[0] = np.sqrt(e[0]*t[0])
k[0] = e[0]*t[0]
em[0] = e[0]
tm[0] = t[0]
lm[0] = np.sqrt(em[0]*tm[0])
km[0] = em[0]*tm[0]


# SIMULATION SECTION
#loop over timesteps for simulation
for ii in range(1,numTimeSteps,1):
    
    #########################################
    #UNCOMMENT THESE LINES TO PERFORM RANDOM TRADES. CHANGE MOD 
    #ARGUMENT TO ADD/REMOVE LIQUIDITY ON CERTAIN STEPS.
    # #every 10th time step add or remove liquidity
    # if np.mod(ii,10000)==0:
    #     addOrRemove = rd.random()
    #     if addOrRemove>=0.5 or ii <= 10:
    #         [e[ii],t[ii],l[ii]] = addLiquidity(1, e[ii-1], t[ii-1], l[ii-1])
    #     elif addOrRemove<0.5 and ii > 10:
    #         [e[ii],t[ii],l[ii]] = removeLiquidity(0.1*l[ii-1], e[ii-1], t[ii-1], l[ii-1])
    # #all the steps in between perform a trade on x or y        
    # else:
    #     spendEorT = rd.choice(myRanChoice)
    #     delta_e = 0.01
    #     delta_t = 10
    #     #choice 1, trader sells e, receives t
    #     if spendEorT == 1 and delta_e > 0:
    #         [e[ii],t[ii]] = ethToToken(delta_e,e[ii-1],t[ii-1])
            
    #     #choice 2, trader buys t, spends e
    #     elif spendEorT == 2 and delta_t > 0  and delta_t < t[ii-1]:
    #         [e[ii],t[ii]] = ethToToken2(delta_t,e[ii-1],t[ii-1])
            
    #     #choice 3, trader sells t, receives e
    #     elif spendEorT == 3 and delta_t > 0:
    #         [e[ii],t[ii]] = tokenToEth(delta_t,e[ii-1],t[ii-1])
            
    #     #choice 4, trader buys e, spends t   
    #     elif spendEorT == 4 and delta_e > 0  and delta_e < e[ii-1]:
    #         [e[ii],t[ii]] = tokenToEth2(delta_e,e[ii-1],t[ii-1])
          
    #     #if none of the above conditions are met...    
    #     else:
    #         [e[ii],t[ii]] = [e[ii-1],t[ii-1]]    
    #########################################


    #########################################
    #COMMENT OR UNCOMMENT TO HAVE BLACK SWAN EVENT IN MARKET
    if ii == 40:
        em[ii-1] = 1.5
        tm[ii-1] = km[ii-1]/em[ii-1]
    #########################################
    
    
    #########################################
    #ARBITGRAGE SECTION. NOTE THE SWAPPING OF e AND t IN FUNCTION CALLS...
    #check arbitrage on asset e bought from market and sold to pool.
    if (1-(tm[ii-1]*e[ii-1])/((1-0.002)*(1-0.003)*em[ii-1]*t[ii-1]))>0:
        [e[ii],t[ii],em[ii],tm[ii]] = arbMToP_e(e[ii-1],t[ii-1],em[ii-1],tm[ii-1])
        
    #check arbitrage on asset e bought from pool and sold to market.    
    elif (1-(t[ii-1]*em[ii-1])/((1-0.002)*(1-0.003)*e[ii-1]*tm[ii-1]))>0:
        [em[ii],tm[ii],e[ii],t[ii]] = arbMToP_e(em[ii-1],tm[ii-1],e[ii-1],t[ii-1])
        
    #check arbitrage on asset t bought from market and sold to pool.
    elif (1-(t[ii-1]*em[ii-1])/((1-0.002)*(1-0.003)*e[ii-1]*tm[ii-1]))>0:
        [t[ii],e[ii],tm[ii],em[ii]] = arbMToP_e(t[ii-1],e[ii-1],tm[ii-1],em[ii-1])
        
    #check arbitrage on asset t bought from pool and sold to market.     
    elif (1-(tm[ii-1]*e[ii-1])/((1-0.002)*(1-0.003)*em[ii-1]*t[ii-1]))>0:
        [tm[ii],em[ii],t[ii],e[ii]] = arbMToP_e(tm[ii-1],em[ii-1],t[ii-1],e[ii-1])
    
    #if no arb opportunity exists    
    else:
        [em[ii],tm[ii]] = [em[ii-1],tm[ii-1]]
        [e[ii],t[ii]] = [e[ii-1],t[ii-1]]
    
    #########################################
    #calculate new l's and k's..

    l[ii] = np.sqrt(e[ii]*t[ii])
    k[ii] = e[ii]*t[ii]
    lm[ii] = np.sqrt(em[ii]*tm[ii])
    km[ii] = em[ii]*tm[ii]


#########################################
#plotting section
fig = make_subplots(rows=4, cols=1)
fig.add_trace(go.Scatter(x=steps, y=e, name='ETH in pool'), row=1,col=1)
fig.update_xaxes(title_text='Time Steps',row=1)
fig.update_yaxes(title_text='ETH',row=1)    

fig.add_trace(go.Scatter(x=steps, y=em, name='ETH in market'), row=2,col=1)
fig.update_xaxes(title_text='Time Steps',row=2)
fig.update_yaxes(title_text='ETH',row=2)  

fig.add_trace(go.Scatter(x=steps, y=k/e**2, name='TKN/ETH pool'), row=3,col=1)
fig.add_trace(go.Scatter(x=steps, y=km/em**2, name='TKN/ETH market'), row=3,col=1)
fig.update_xaxes(title_text='Time Steps',row=3)
fig.update_yaxes(title_text='TKN/ETH',row=3) 

fig.add_trace(go.Scatter(x=steps, y=e*tm/em + t, name='pool liq value in TKN'), row=4,col=1)
fig.update_xaxes(title_text='Time Steps',row=4)
fig.update_yaxes(title_text='TKN',row=4) 

fig.layout.title = '...'    
fig.show()
#########################################


