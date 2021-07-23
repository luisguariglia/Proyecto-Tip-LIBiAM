def estilos_tree_widget_graficas():
    return """
    QTreeWidget{
        margin-bottom:6px;
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
        margin-left:7px;
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