# ui/style.py

COSMIC_STYLE = """
/* Общий фон и текст */
QMainWindow, QDialog, QWidget {
    background-color: #0F1426;
    color: #C0D0FF;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* Заголовки групп */
QGroupBox {
    border: 1px solid #4A5B7C;
    margin-top: 10px;
    color: #A0B0D0;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

/* Кнопки */
QPushButton {
    background-color: #2A3B5C;
    color: #E0E0FF;
    border: 1px solid #4A5B7C;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3A4B6C;
}
QPushButton:pressed {
    background-color: #1A2B4C;
}
QPushButton:disabled {
    background-color: #1A1F2B;
    color: #607080;
}

/* Метки */
QLabel {
    color: #C0D0FF;
}

/* Спинбоксы и чекбоксы */
QSpinBox, QCheckBox {
    background-color: #1A2332;
    color: #C0D0FF;
    border: 1px solid #4A5B7C;
    padding: 4px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
}

/* Нижняя информационная панель */
#InfoBar {
    background-color: #0B0F1F;
    color: #FFFFFF;
    padding: 5px;
    font-weight: bold;
    border-top: 1px solid #2A3B5C;
}

/* Главное меню — заголовок */
#MainMenuTitle {
    font-size: 20px;
    font-weight: bold;
    color: #6ACAFE;
    margin: 20px 0;
}
"""