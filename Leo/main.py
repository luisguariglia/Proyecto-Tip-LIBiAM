import numpy as np
import matplotlib.pyplot as plt

x = [1,2,3,4,5]
y = [0.000001,0.000002,0.000003,0.000004,0.000005]
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
axs.plot(x,y)
plt.tight_layout()
exponent = axs.yaxis.get_offset_text().get_text()
print('exponent:', int(exponent.split('e−')[1]))
plt.show()