import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import *
import ctypes
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon, QFont
import GPUtil

is_icon = True
is_text = True

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = QApplication([])
window = QWidget()
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
window.setGeometry(1300, 1020, 1, 1)

app_icon = QIcon(resource_path("icon.ico"))
app.setWindowIcon(app_icon)

is_dark_theme = True
old_pos = None

layV = QHBoxLayout()
cpu = QLabel()
ram = QLabel()
gpu = QLabel()
font = QFont("Bold", 10)
cpu.setFont(font)
gpu.setFont(font)
ram.setFont(font)
layV.addWidget(cpu)
layV.addWidget(ram)
layV.addWidget(gpu)
window.setLayout(layV)
cpu.setAttribute(Qt.WA_TransparentForMouseEvents)
ram.setAttribute(Qt.WA_TransparentForMouseEvents)
gpu.setAttribute(Qt.WA_TransparentForMouseEvents)

# Установим фиксированную высоту для виджетов
#cpu.setFixedHeight(35)
#ram.setFixedHeight(35)
#gpu.setFixedHeight(35)

# Установим политику размера
cpu.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
ram.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
gpu.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

# Установим отступы и spacing для layout
#layV.setContentsMargins(5, 0, 5, 0)
#layV.setSpacing(5)

def apply_theme():
    if is_dark_theme:
        window.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 1px solid #444;
                border-radius: 3px;
            }
            QLabel {
                color: white;
                background-color: transparent;
                padding: 2px 5px;
            }
        """)
    else:
        window.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }
            QLabel {
                color: black;
                background-color: transparent;
                padding: 2px 5px;
            }
        """)

apply_theme()

def get_gpu_usage():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "No GPU"
        max_load = max(gpu.load * 100 for gpu in gpus)
        return f"{max_load:.1f}%"
    except Exception as e:
        return "N/A"

def update():
    global is_icon
    cpu_icon = resource_path("images/cpu_white.png") if is_dark_theme else resource_path("images/cpu_black.png")
    ram_icon = resource_path("images/ram_white.png") if is_dark_theme else resource_path("images/ram_black.png")
    gpu_icon = resource_path("images/gpu_white.png") if is_dark_theme else resource_path("images/gpu_black.png")
    
    if is_icon:
        cpu.setText(f'<img src="{cpu_icon}" width="30" height="30"> Cpu: {psutil.cpu_percent()}%')
        ram.setText(f'<img src="{ram_icon}" width="30" height="30"> Ram: {psutil.virtual_memory().percent}%')
        gpu.setText(f'<img src="{gpu_icon}" width="30" height="30"> Gpu: {get_gpu_usage()}%')  # Исправлено: было Ram, стало Gpu
    else:
        cpu.setText(f'Cpu: {psutil.cpu_percent()}%')
        ram.setText(f'Ram: {psutil.virtual_memory().percent}%')
        gpu.setText(f'Gpu: {get_gpu_usage()}%')
    resize_window()

def resize_window():
    width = 5 + 5  # left + right margins
    visible_widgets = [w for w in [cpu, ram, gpu] if w.isVisible()]
    if visible_widgets:
        for w in visible_widgets:
            w.adjustSize()  # Обновляем размер виджета под содержимое
            width += w.width()
        width += 5 * (len(visible_widgets) - 1)  # spacing между виджетами
    window.resize(width, window.height())

def mousePressEvent(event):
    global old_pos
    if event.button() == Qt.LeftButton:
        old_pos = event.globalPos()
    elif event.button() == Qt.RightButton:
        show_context_menu(event.globalPos())

def mouseMoveEvent(event):
    global old_pos
    if old_pos and event.buttons() == Qt.LeftButton:
        delta = event.globalPos() - old_pos
        window.move(window.pos() + delta)
        old_pos = event.globalPos()

def mouseReleaseEvent(event):
    global old_pos
    if event.button() == Qt.LeftButton:
        old_pos = None

def event(event):
        if event.type() == QEvent.WindowDeactivate:
            window.raise_()
            window.activateWindow()
        return super().event(event)

def mouseDoubleClickEvent(event):
        window.close()
        app.quit()

def windowEvent(event):
    if event.type() == QEvent.WindowDeactivate:
        window.raise_()
        window.activateWindow()
    return QWidget.event(window, event)

def cpu_change(checked):
    if checked:
        cpu.show()
    else:
        cpu.hide()
    resize_window()

def ram_change(checked):
    if checked:
        ram.show()
    else:
        ram.hide()
    resize_window()

def gpu_change(checked):
    if checked:
        gpu.show()
    else:
        gpu.hide()
    resize_window()

def icon_change(checked):
    global is_icon
    if checked:
        is_icon = True
    else:
        is_icon = False
    update()
    resize_window()

def text_change(checked):
    global is_text
    if checked:
        is_text = True
        font = QFont("Bold", 10)
        cpu.setFont(font)
        gpu.setFont(font)
        ram.setFont(font)
    else:
        is_text = False
        font = QFont("Bold", 14)
        cpu.setFont(font)
        gpu.setFont(font)
        ram.setFont(font)

    resize_window()

def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    apply_theme()
    update() 

def show_context_menu(position):
    menu = QMenu()
    
    theme_action = QAction("Тёмная тема" if not is_dark_theme else "Светлая тема", window)
    theme_action.triggered.connect(toggle_theme)
    menu.addAction(theme_action)
    
    menu.addSeparator()
    
    cpu_action = QAction("CPU", window)
    cpu_action.setCheckable(True)
    cpu_action.setChecked(cpu.isVisible())
    cpu_action.toggled.connect(cpu_change)
    menu.addAction(cpu_action)

    ram_action = QAction("RAM", window)
    ram_action.setCheckable(True)
    ram_action.setChecked(ram.isVisible())
    ram_action.toggled.connect(ram_change)
    menu.addAction(ram_action)
    
    gpu_action = QAction("GPU", window)
    gpu_action.setCheckable(True)
    gpu_action.setChecked(gpu.isVisible())
    gpu_action.toggled.connect(gpu_change)
    menu.addAction(gpu_action)

    icon_action = QAction("Иконки", window)
    icon_action.setCheckable(True)
    icon_action.setChecked(is_icon)
    icon_action.toggled.connect(icon_change)
    menu.addAction(icon_action)

    text_action = QAction("Мини текст", window)
    text_action.setCheckable(True)
    text_action.setChecked(is_text)
    text_action.toggled.connect(text_change)
    menu.addAction(text_action)
    
    menu.addSeparator()
    
    exit_action = menu.addAction("Выход")
    
    action = menu.exec_(position)
    if action == exit_action:
        window.close()
        app.quit()

window.mousePressEvent = mousePressEvent
window.mouseMoveEvent = mouseMoveEvent
window.mouseReleaseEvent = mouseReleaseEvent
window.mouseDoubleClickEvent = mouseDoubleClickEvent
window.windowEvent = windowEvent

timer = QTimer()
timer.timeout.connect(update)
timer.start(1000)

update()
resize_window()

window.show()
app.exec_()