import numpy as np
b = np.array([(1,2),(2,3)])
a = np.array([(1,1)])
c = np.concatenate((a,b))
print(c)