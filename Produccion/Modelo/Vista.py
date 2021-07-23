class Vista:
    def __init__(self,tree_widget_item,widget,index):
        self.__tree_widget_item = tree_widget_item
        self.__widget = widget
        self.__index = index
        self.__graficas = []
        self.__canvas = None
        self.__nav_toolbar = None
        self.__scroll = None

    def get_tree_widget_item(self):
        return self.__tree_widget_item

    def set_tree_widget_item(self,nuevo_widget_item):
        self.__tree_widget_item = nuevo_widget_item

    def get_widget(self):
        return self.__widget

    def set_widget(self,widget):
        self.__widget = widget

    def get_index(self):
        return self.__index

    def set_index(self,index):
        self.__index = index

    def get_canvas(self):
        return self.__canvas

    def set_canvas(self,canvas):
        self.__canvas = canvas

    def get_graficas(self):
        return self.__graficas

    def get_nav_toolbar(self):
        return self.__nav_toolbar

    def set_nav_toolbar(self,nav_toolbar):
        self.__nav_toolbar = nav_toolbar

    def get_scroll(self):
        return self.__scroll

    def set_scroll(self,scroll):
        self.__scroll = scroll

    def agregar_grafica(self,nueva_grafica):
        self.__graficas.append(nueva_grafica)

    @staticmethod
    def get_vista_by_widget(vistas,widget):
        vista_aux = None
        for vista in vistas:
            if widget == vista.get_widget():
                vista_aux = vista
                break
        return vista_aux