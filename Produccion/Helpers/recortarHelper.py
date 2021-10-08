from matplotlib import pyplot as plt

def dibujarLineaEnGrafica(axes,event,texto,grafica):
    axes.annotate(texto + "{0:.2f}".format(event.xdata),xy=(event.xdata, event.ydata),xytext=(event.xdata, 0))
    ancho = (grafica.getLimitesTiempo()[1] - grafica.getLimitesTiempo()[0]) / 1000
    circle1 = plt.Rectangle((event.xdata, 0), ancho, 9999999, color='r', alpha=0.5)
    axes.add_patch(circle1)