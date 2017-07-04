import matplotlib.pyplot as plt
import pickle
import numpy as np
from scipy import signal

data = pickle.load(open('data2.pkl', 'rb'))
data = [data[0], data[1], data[3]]


def preprocessing(y):
    y_mi = []
    for i in xrange(0, len(y)-5):
        t = y[i:i+5]
        t.sort()
        y_mi.append(t[2])

    y = y_mi
    y_mi = []
    for i in xrange(0, len(y)-5):
        t = y[i:i+5]
        tt = sum(t)/float(len(t))
        y_mi.append(tt)
    return y_mi

p = np.array(preprocessing(data[0]))
h = np.array(preprocessing(data[1]))
t = np.array(preprocessing(data[2]))
result = p / t

# '''
plt.plot(range(len(result)), result)
plt.show()
# '''