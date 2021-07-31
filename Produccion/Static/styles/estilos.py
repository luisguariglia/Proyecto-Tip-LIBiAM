def estilos_tree_widget_graficas():
    return """
    QTreeWidget{
        margin-bottom:6px;
        background-color:white;

    }

    QTreeWidget::branch:has-siblings:!adjoins-item {
        border-image: url(Static/img/vline.png) 0;    
    }

    QTreeWidget::branch:has-siblings:adjoins-item {
        border-image: url(Static/img/branch-more.png) 0;
    }

    QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
        border-image: url(Static/img/branch-end.png) 0;
    }

    QTreeWidget::branch:has-children:!has-siblings:closed,
    QTreeWidget::branch:closed:has-children:has-siblings {
        border-image: none;image: url(Static/img/branch-closed.png);
    }

    QTreeWidget::branch:open:has-children:!has-siblings,
    QTreeWidget::branch:open:has-children:has-siblings{
        border-image: none;image: url(Static/img/branch-open.png);
    }
    """


def estilos_tree_widget_vistas():
    return """
    QTreeWidget::branch:has-children:!has-siblings:closed,
    QTreeWidget::branch:closed:has-children:has-siblings {
        border-image: none;image: url(Static/img/branch-closed.png);
    }

    QTreeWidget::branch:open:has-children:!has-siblings,
    QTreeWidget::branch:open:has-children:has-siblings{
        border-image: none;image: url(Static/img/branch-open.png);
    }
    """


def estilos_toolbar_archvos_csv():
    return """
    QToolBar{
        border:0px;
        margin-right:1px;
    }

    QToolButton{
        margin-left:6px;
        border-radius:2px;
        border:9px;
    }

    QToolButton:hover{
        background-color:#E0E0E0;
    }
    """


def estilos_combobox_archivos_csv():
    return """
    QComboBox {
            border: 0px;
            font-size: 12px;
            color:#757575;
            border-radius: 3px;
            background-color: white;
            padding: 1px 18px 1px 6px;
            min-width: 6em;
    }

    QComboBox:editable {
        background-color: white;
    }

    QComboBox:!editable, QComboBox::drop-down:editable {
        background-color:white;
    }

    QComboBox:!editable:on, QComboBox::drop-down:editable:on {
        background-color:white;
    }

    QComboBox:on {
        padding-top: 3px;
        padding-left: 4px;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        background-color:white;
        border-left-width: 0px;
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }

    QComboBox::down-arrow {
        image: url(Static/img/branch-open.png);
    }

    QComboBox::down-arrow:on {
        top: 1px;
        left: 1px;
    }
    """


def estilos_widget_inicio():
    return """
    QWidget{
        border:2px solid #FAFAFA;
    }


    """


def estilos_widget_header_inicio():
    return """
        QWidget{
            border-bottom:0px;
        }

        QLabel{
            margin:0px;
            padding:0px;
            border:0px;
        }
    """


def estilos_widget_content():
    return """
        QWidget{
            margin:0px;
            padding:0px;
            background-color:#004A82;
            border:0px;
        }
    """

def estilos_btn_aplicar_a_todas():
    return """
        QPushButton{
            color:#FAFAFA;
            font:bold 9px;
            border:1px solid #114980;
            background-color:#114980;
            border-radius: 2px;
            padding:6px;
        }
        
        QPushButton:hover{
           color:#114980;
           background-color:#F5F5F5;
        }
        
        QPushButton:pressed{
           background-color:#E0E0E0;
        }
    """


def estilos_spinbox_filtros():
    return """
        QSpinBox{
            
            border:1px solid #757575;
            border-radius:2px;
            padding: 5px; 
            background : #F5F5F5;
            
         }
         
         QSpinBox::hover{
            border:1px solid #424242;
            background : #EEEEEE;
         }
        
         QSpinBox::down-arrow {
            image: url(Static/img/unnamed.png);
            width: 7px;
            height: 7px;
        }
        
        QSpinBox::up-arrow {
            image: url(Static/img/up-arrow.png);
            width: 7px;
            height: 7px;
        }
        
        QSpinBox::down-button {
            background-color:#E0E0E0;
        }
        
        QSpinBox::up-button {
            border-top-right-radius:2px;
            border-bottom-right-radius:2px;
            background-color:#E0E0E0;
        }
        
        QSpinBox::up-arrow:hover {
        
           image: url(Static/img/up-arrow-hover.png);
        }
        
        QSpinBox::up-button:hover {
            background-color:#bdbdbd;
        }
        
        QSpinBox::down-arrow:hover {
        
           image: url(Static/img/down-arrow-hover.png);
        }
        
        QSpinBox::down-button:hover {
            background-color:#bdbdbd;
        }
        
        QSpinBox::up-arrow:pressed {
        
           image: url(Static/img/up-arrow-pressed.png);
        }
        
        QSpinBox::up-button:pressed {
            background-color:#9E9E9E;
        }
        
        QSpinBox::down-arrow:pressed {
        
           image: url(Static/img/down-arrow-pressed.png);
        }
        
        QSpinBox::down-button:pressed {
            background-color:#9E9E9E;
        }
            
    """


def estilos_double_spinbox_filtros():
    return """
        QDoubleSpinBox{

            border:1px solid #757575;
            border-radius:2px;
            padding: 5px; 
            background : #F5F5F5;

         }

         QDoubleSpinBox::hover{
            border:1px solid #424242;
            background : #EEEEEE;
         }

         QDoubleSpinBox::down-arrow {
            image: url(Static/img/unnamed.png);
            width: 7px;
            height: 7px;
        }

        QDoubleSpinBox::up-arrow {
            image: url(Static/img/up-arrow.png);
            width: 7px;
            height: 7px;
        }

        QDoubleSpinBox::down-button {
            background-color:#E0E0E0;
        }

        QDoubleSpinBox::up-button {
            border-top-right-radius:2px;
            border-bottom-right-radius:2px;
            
            background-color:#E0E0E0;
        }

        QDoubleSpinBox::up-arrow:hover {

           image: url(Static/img/up-arrow-hover.png);
        }

        QDoubleSpinBox::up-button:hover {
            background-color:#bdbdbd;
        }

        QDoubleSpinBox::down-arrow:hover {

           image: url(Static/img/down-arrow-hover.png);
        }

        QDoubleSpinBox::down-button:hover {
            background-color:#bdbdbd;
        }

        QDoubleSpinBox::up-arrow:pressed {

           image: url(Static/img/up-arrow-pressed.png);
        }

        QDoubleSpinBox::up-button:pressed {
            background-color:#9E9E9E;
        }

        QDoubleSpinBox::down-arrow:pressed {

           image: url(Static/img/down-arrow-pressed.png);
        }

        QDoubleSpinBox::down-button:pressed {
            background-color:#9E9E9E;
        }

    """


def estilos_combobox_filtro():
    return """
    QComboBox {
        font:12px bold;
        padding: 5px;
        border:1px solid #757575;
        border-radius:2px;
        background : #F5F5F5;
    }
    
    QComboBox:hover {

            border:1px solid #424242;
            background : #EEEEEE;
    }
    
    
    QComboBox::drop-down{
        background-color:#E0E0E0;
    }
    
    QComboBox::drop-down::hover{
        background-color:#bdbdbd;
    }
    
    QComboBox::drop-down::pressed{
        background-color:#9E9E9E;
    }
    
    QComboBox::down-arrow {
        image: url(Static/img/down-arrow-combo-filtro.png);
    }
    
    QComboBox::down-arrow::hover {
        image: url(Static/img/down-arrow-combo-filtro-hover.png);
    }
    
    QComboBox::down-arrow::pressed {
        image: url(Static/img/down-arrow-combo-filtro-pressed.png);
    }

    """

