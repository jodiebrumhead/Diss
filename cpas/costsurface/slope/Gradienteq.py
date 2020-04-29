import numpy as np
import matplotlib.pyplot as plt

"""
Function to calculate equation from Irmischer and Clarke (2018). This models walking speed based on slope.
"""
def slopespeed(a):
    return 0.11 + np.exp(((-(a + 5)**2)/(2*30**2)))


"""
Function to calculate the impact of slope on walking speed. 

Finds mean of speed for both upwards and downwards of a slope (%).
This is then calculated as a percentage of the speed for 0 slope (i.e. flat)
"""
def slopeimpact(b):
    return (((0.5*(slopespeed(+b)+slopespeed(-b))/slopespeed(0)) * 100))


if __name__ == '__main__':
    """
    A print statement to demonstrate the results of each of the equations
    """

    for i in range(10):
        print(i, slopespeed(-i), slopespeed(+i), slopeimpact(i))


    """
    Produce a graph of the slopeimpact() function equation. 
    """
    x = []
    y = []

    for i in range(501):
        x.append(i)
        y.append(slopeimpact(i))

    plt.plot(x,y)
    plt.grid()
    plt.xlabel('Slope (%)')
    plt.ylabel('Speed Impact (%)')
    plt.savefig('slopeimpactgraph.png')