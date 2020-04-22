import math
print(2*30**2)

print((2*30)*(2*30))

def dicks(x):
    answer = 0.11 + math.exp(((-(x + 5)**2)/(2*30**2)))
    return answer


for i in range(-100,101):
    print(i, dicks(i))



# equation =  (0.11 + e^(-(x + 5)**2/(2*30**2)))/(0.11 + e^(-(0 + 5)**2/(2×30**2)))×100


#eq1 = ((0.5*((0.11 + math.exp(((-(+x + 5)**2)/(2*30**2)))) + (0.11 + math.exp(((-(-x + 5)**2))/(2*30**2))))) / eq0) * 100

#print(eq1)