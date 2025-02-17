# -*- coding: utf-8 -*-
"""Torch Simplex-Matrix.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qWuWfsvMbIdB8v_N92Tvmkcv-Tzh8xuZ
"""

import numpy as np
import torch

"""## Implementation of The Simplex Algorithm via Matrix Operations

The following code implements the Simplex method with matrix operations, as opposed to the tableau method.  

We begin by writing out a constrained optimization problem in *standard form* below.  The matrix $A$ holds the coefficients of the inequality constraints, the vector $b$ is the vector of solutions, and the vector $c$ holds the coefficients of the variables of the objective function that is being optimized.
"""

# User Defined Input

# Example Input
A = np.array([[-2, 1, 1, 0, 0],
             [-1, 2, 0, 1, 0],
             [1, 0, 0, 0, 1]])

b = np.array([2, 7, 3])

c = np.array([-1, -2, 0, 0, 0])





"""Now, we continue to establish the function ``Simplex`` that solves a linear constrained optimization problem using a matrix method implementation of the Simplex Algorithm."""

def Simplex(A, b, c):
    '''Takes input vars, computs corresponding values,
    then uses while loop to iterate until a basic optimal solution is reached.
    RETURNS: cbT, cbIndx, cnT, cnIndx, bHat, cnHat.
    cbT, cbIndex is final basic variable values, and indices
    cnT, cnIndex is final nonbasic variable values and indices
    bHat is final solution values,
    cnHat is optimality condition'''


    At = torch.from_numpy(A)
    bt = torch.from_numpy(b)
    ct = torch.from_numpy(c)


    if torch.cuda.is_available():
        dev = "cuda:0"
    else:
        dev = "cpu"
    device = torch.device(dev)
    At = At.to(device)
    bt = bt.to(device)
    ct = ct.to(device)

    #sizes of basic and nonbasic vectors
    basicSize = A.shape[0] # number of constraints, m
    nonbasicSize = A.shape[1] - basicSize #n-m, number of variables

    # global index tracker of variables of basic and nonbasic variables (objective)
    # that is, index 0 corresponds with x_0, 1 with x_1 and so on.  So each index corresponds with a variable
    cindx   = [i for i in range(0, len(c))]
    cindx_t = [i for i in range(0, len(ct))]

    #basic variable coefficients
    cbT    = np.array(c[nonbasicSize:])
    #cbT_t  = torch.tensor(ct[nonbasicSize:])
    cbT_t  = ct[nonbasicSize:].clone() 

    #nonbasic variable coefficients
    cnT = np.array(c[:nonbasicSize])
    #cnT_t = torch.tensor(ct[:nonbasicSize])
    cnT_t = ct[:nonbasicSize].clone()
    # run core simplex method until reach the optimal solution
    num = 0
    while True:

        #print('iteration +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ',num)
        # keep track of current indices of basic and non-basic variables
        cbIndx = cindx[nonbasicSize:]
        cnIndx = cindx[:nonbasicSize]
        cbIndx_t = cindx_t[nonbasicSize:]
        cnIndx_t = cindx_t[:nonbasicSize]
        #print('cnT,cnT_t,cindx,cindx_t ',num, cnT, cnT_t, cindx, cindx_t)

        #/
        #basis matrix
        B = A[:, cbIndx]
        Bt = At[:, cbIndx_t]

        Binv   = np.linalg.inv(B)
        Binv_t = torch.linalg.inv(Bt.double())

        # nonbasic variable matrix
        N = A[:, cnIndx]
        Nt = At[:, cnIndx_t]

        # bHat, the values of the basic variables
        # recall that at the start the basic variables are the slack variables, and
        # have values equal the vector b (as primary variables are set to 0 at the start)
        bHat = Binv @ b
        bHat_t = torch.matmul(Binv_t,bt.double())
        yT = cbT @ Binv
        yT_t = torch.matmul(cbT_t.double(),Binv_t)

        # use to check for optimality, determine variable to enter basis
        cnHat = cnT - (yT @ N)
        cnHat_t = cnT_t - torch.matmul(yT_t,Nt.double())
        # find indx of minimum value of cnhat, this is the variable to enter the basis
        cnMinIndx   = np.argmin(cnHat)
        cnMinIndx_t = torch.argmin(cnHat_t)


        # break out of loop, returning values if all values of cnhat are above 0
        # for Torch: (cnHat_t >0).all()
        if(all(i>=0 for i in cnHat)):
            # use cbIndx to get index values of variables in bHat, and the corresponding index
            # values in bHat are the final solution values for each of the corresponding variables
            # ie value 0 in dbIndx corresponds with first variable, so whatever the index for the 0 is
            # is the index in bHat that has the solution value for that variable.
            return cbT, cbIndx, cnT, cnIndx, bHat, cnHat,cbT_t, cbIndx_t, cnT_t, cnIndx_t, bHat_t, cnHat_t

        # this is the index for the column of coeffs in a for the given variable
        indx = cindx[cnMinIndx]
        indx_t = cindx_t[cnMinIndx_t]

        Ahat   = Binv @ A[:, indx]
        Ahat_t = torch.matmul(Binv_t,At[:, indx_t].double())

        # now we want to iterate through Ahat and bHat and pick the minimum ratios
        # only take ratios of variables with Ahat_i values greater than 0
        # pick smallest ratio to get variable that will become nonbasic.
        ratios   = []
        ratios_t = []
        for i in range(0, len(bHat)):
            Aval = Ahat[i]
            Bval = bHat[i]
            Aval_t = Ahat_t[i]
            Bval_t   = bHat_t[i]

            # don't look at ratios with val less then or eqaul to 0, append to keep index
            if Aval <= 0 or Aval_t <= 0:
                ratios.append(10000000)
                ratios_t.append(10000000)
                continue
            ratios.append(Bval / Aval)
            ratios_t.append(Bval_t / Aval_t)

        ratioMinIndx = np.argmin(ratios)
        ratios_t = torch.tensor(ratios_t)
        ratioMinIndx_t = torch.argmin(ratios_t)

        #print('cnT,cnT_t,cbT,cbT_t ',cnT,cnT_t,cbT,cbT_t)
        #switch basic and nonbasic variables using the indices.
        cnT[cnMinIndx], cbT[ratioMinIndx] = cbT[ratioMinIndx], cnT[cnMinIndx]

        tmp1                  = torch.clone(cbT_t[ratioMinIndx_t])
        tmp2                  = torch.clone(cnT_t[cnMinIndx_t])
        cnT_t[cnMinIndx_t]    = tmp1
        cbT_t[ratioMinIndx_t] = tmp2
        # switch global index tracker indices
        cindx[cnMinIndx], cindx[ratioMinIndx + nonbasicSize] = cindx[ratioMinIndx + nonbasicSize], cindx[cnMinIndx]


        ###################################
        cindx_t = torch.tensor(cindx_t)
        tmp1 = torch.clone(cindx_t[ratioMinIndx_t + nonbasicSize]),
        tmp2 = torch.clone(cindx_t[cnMinIndx_t])

        cindx_t[cnMinIndx_t] = tmp1[0]
        cindx_t[ratioMinIndx_t + nonbasicSize] = tmp2
        #print('cnT,cnT_t,cindx,cindx_t ',num,cnT,cnT_t,cindx,cindx_t)
        num = num + 1
        qq = 0
        # now repeat the loop

Ai = np.array([[6, 3, 1, 4],
       [2, 4, 5, 1],
       [1, 2, 4, 3]])

bi = np.array([252, 144,  80])

ci = np.array([48, 33, 16, 22])

N,M = A.shape
N = 5
M = 100
As = np.abs(np.random.random((N,M)))
bs = np.abs(np.random.random(N))
cs = np.abs(np.random.random(M))

cbT, cbIndx, cnT, cnIndx, bHat, cnHat, cbT_t, cbIndx_t, cnT_t, cnIndx_t, bHat_t, cnHat_t = Simplex(As, bs, cs)
d_cnIndx = np.max(np.abs(cnIndx-cnIndx_t.numpy()))
bHat_t = bHat_t.to('cpu')
d_bHat   = np.max(np.abs(bHat-bHat_t.numpy()))
print('differerence in cnIndx, bHat ',d_cnIndx,d_bHat)

"""In the following we proceed to test the function with different constrained optimization problems."""

# example test
A = np.array([[2, 1, 1, 0, 0],
             [2, 3, 0, 1, 0],
             [3, 1, 0, 0, 1]])
c = np.array([-3, -2, 0, 0, 0])
b = np.array([18, 42, 24])

Simplex(A, b, c)

# another example test
A = np.array([[1, 1, 1, 1, 0, 0],
            [-1, 2, -2, 0, 1, 0],
            [2, 1, 0, 0, 0, 1]])

b = np.array([4, 6, 5])
c = np.array([-1, -2, 1, 0, 0, 0])

Simplex(A, b, c)

"""As seen above, the function ``Simplex`` outputs the correct values.  ``Simplex`` returns more information than necessary (it does not just return the solution), but it can be useful to see the final values of all the key matrices it uses in the algorithm, so we may gain an intuition into what is going on."""
