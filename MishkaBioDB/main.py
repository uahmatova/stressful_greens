from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import BorderImage, Color, Rectangle, SmoothRoundedRectangle, RenderContext, RoundedRectangle
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.atlas import Atlas
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.dropdown import DropDown
from kivy.properties import NumericProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from box1 import Module1    #подгрузила окошко модуля из файла для модуля
import ctypes

Mtext_med = '../MTest/Montserrat-Medium.ttf'
Mtext_reg = '../MTest/Montserrat-Regular.ttf'
Mtext_bold = '../MTest/Montserrat-Bold.ttf'
Mtext_semibold = '../MTest/Montserrat-SemiBold.ttf'
dark_green = (44/255, 57/255, 57/255, 1)
light_green = (221/255, 230/255, 217/255, 1)
smoky_green = (156/255, 163/255, 154/255, 1)
ghosty_green = (219/255, 231/255, 216/255, 1)
dark_red = (127/255, 13/255, 0/255, 1)
all_max_width = 360 * 0.8 + 10
all_max_height = 800 * 0.8


#===.===.===.=== Шаблоны элементов. Используются в файле main.kv ===.===.===.===
class ModuleButtonLabel(ButtonBehavior, Label):
    markup = True
    halign = 'center'
    font_size = 19
    max_width = all_max_width + 50  # максимальная ширина кнопки
    max_height = 78  # максимальная высота кнопки
    font_name = Mtext_med
    multiline = True
    def __init__(self, **kwargs):
        super(ModuleButtonLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=dark_green)
            self.rect = RoundedRectangle(pos=self.pos, radius=[5,])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class ButtonLabelMed(ButtonBehavior, Label):
    markup = True
    halign = 'center'
    font_size = 24
    max_width = all_max_width + 25
    max_height = 100
    font_name = Mtext_reg
    def __init__(self, **kwargs):
        super(ButtonLabelMed, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=dark_green)
            self.rect = RoundedRectangle(pos=self.pos, radius=[10,])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class ButtonLabel(ButtonBehavior, Label):
    markup = True
    halign = 'center'
    font_size = 21
    max_width = all_max_width + 75
    max_height = 70
    font_name = Mtext_semibold
    def __init__(self, **kwargs):
        super(ButtonLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=dark_green)
            self.rect = RoundedRectangle(pos=self.pos, radius=[10,])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class SmallButtonLabel(ButtonBehavior, Label):
    markup = True
    font_size = 20
    max_width = all_max_width # максимальная ширина кнопки
    max_height = 80  # максимальная высота кнопки
    font_name = Mtext_med
    color=smoky_green
    def __init__(self, **kwargs):
        super(SmallButtonLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=(0,0,0,0))
            self.rect = Rectangle(pos=self.pos)
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class JustLabel(Label):
    markup=True
    text_size=(300, None)
    font_size= 30
    halign='center'
    valign='bottom'
    max_width=all_max_width
    max_height=80
    color=dark_green
    font_name=Mtext_semibold

    def __init__(self, **kwargs):
        super(JustLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color:(0, 0, 0, 0) 
            # Color(rgba=light_green)
            # self.rect = RoundedRectangle(pos=self.pos, radius=[10, ])
            # self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class SmallLabel(Label):
    markup=True
    text_size=(300, None)
    font_size=17
    halign='left'
    valign='bottom'
    max_width=all_max_width
    max_height=50
    color=smoky_green
    font_name=Mtext_med#'../MTest/Montserrat-Medium.ttf'

    def __init__(self, **kwargs):
        super(SmallLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=light_green)
            self.rect = RoundedRectangle(pos=self.pos, radius=[10, ])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class HelpLabel(ButtonBehavior, Label):
    markup = True
    halign='left'
    font_size = 19
    max_width = all_max_width
    max_height = 30
    font_name = Mtext_reg
    color = dark_red
    def __init__(self, **kwargs):
        super(HelpLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=(0,0,0,0))
            self.rect = Rectangle(pos=self.pos)
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class InfoLabel(Label):
    markup=True
    halign='left'
    text_size=(300, None)
    font_size=22
    max_width=all_max_width
    max_height=80
    color=dark_green
    font_name=Mtext_reg

    def __init__(self, **kwargs):
        super(InfoLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=(0,0,0,0))
            self.rect = RoundedRectangle(pos=self.pos, radius=[10, ])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height

class NameInfoLabel(Label):
    text_size=(300, None)
    font_size=26
    max_width=all_max_width
    max_height=80
    color=dark_green
    font_name=Mtext_semibold

    def __init__(self, **kwargs):
        super(NameInfoLabel, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=(0,0,0,0))
            self.rect = RoundedRectangle(pos=self.pos, radius=[10, ])
            self.bind(pos=self.schedule_update_rect, size=self.schedule_update_rect)

    def schedule_update_rect(self, instance, value):
        Clock.schedule_once(self.update_rect)
        
    def update_rect(self, dt):
        if self.rect.pos != self.pos or self.rect.size != self.size:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_width(self, instance, value):
        if value > self.max_width:
            self.width = self.max_width

    def on_height(self, instance, value):
        if value > self.max_height:
            self.height = self.max_height            

class CustomDropDown(DropDown):
    pass
#===.===.===.=== Классы страниц. Используются в файле main.kv ===.===.===.===
class RootScreen(ScreenManager):
    pass

class Page1(Screen): #стартовая страница
    pass

class UserPage(Screen): #стартовая страница
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_groups = DropDown()
        self.dropdown_modules = DropDown()
        
    def dropdown_groups_click(self):
        self.dropdown_groups.clear_widgets()        
        data = ['Группа 1', 'Группа2', 'Группа 3', 'Группа4']
        for item in data:
            btn = ButtonLabel(text=item, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_item_g(btn.text))
            self.dropdown_groups.add_widget(btn)
        self.dropdown_groups.open(self.ids.btn_groups)

    def select_item_g(self, text):
        self.ids.btn_groups.text = text
        self.dropdown_groups.dismiss()
        
    def dropdown_modules_click(self):
        self.dropdown_modules.clear_widgets()        
        data = ['Модуль 1', 'Модуль2', 'Модуль 3', 'Модуль 4']
        for item in data:
            btn = ButtonLabel(text=item, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_item_m(btn.text))
            self.dropdown_modules.add_widget(btn)
        self.dropdown_modules.open(self.ids.btn_modules)

    def select_item_m(self, text):
        self.ids.btn_modules.text = text
        self.dropdown_modules.dismiss()


    def toggle(self, *args, **kwargs):
        if kwargs['i'] == 1:           
            self.ids.btn1.state = 'down'
            self.ids.btn2.state = 'normal'
            #MDApp.get_running_app().ips = False
        if kwargs['i'] == 2:           
            self.ids.btn1.state = 'normal'
            self.ids.btn2.state = 'down'

class EnterReg(Screen): #экран регистрации и входа
    pass


#*ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚
#сделан в отдельном файле, переход осуществляется по ссылке из кнопки   
# class Module1(Screen):  #модуль зеленушки
#     #Builder.load_string(db.load_module(1))
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         Builder.load_file('box1.kv')
    
#     def on_enter(self):
#         print("Модуль 1 загружен")
#     pass

#===.===.===.=== Сама приложенька ===.===.===.===
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #defie color scheme
        self.dark_green = dark_green
        self.light_green = light_green
        self.smoky_green = smoky_green
        self.ghosty_green = ghosty_green
        self.dark_red = dark_red
        #define font
        self.Mtext_med = Mtext_med
        self.Mtext_reg = Mtext_reg
        self.Mtext_bold = Mtext_bold
        self.Mtext_semibold = Mtext_semibold
        #dpi, попытка в адаптивность
        self.dpi = Window.dpi
        
    #Пример диалогового окна с кнопкой ОК. Пример вызова - в файле kv с id dialog_here
    #ОТРЕДАЧИЛА СТИЛЬ + настроила динамическую смену текста
    def start_dialog_OK(self, obj, dialog_text=None, instance=None):
        if dialog_text is None:
            dialog_text = "[color=#ffffff][font=../MTest/Montserrat-Bold.ttf]Данные не сохранены.\nПока![/font][/color]"
        self.dialog=MDDialog(
            md_bg_color=self.dark_green,
            height=150,
            text=dialog_text,
            buttons=[
                MDFlatButton(
                    text="ОК",
                    height=30,
                    font_size=15,
                    md_bg_color='white',
                    theme_text_color="Custom",
                    font_name=Mtext_bold,
                    on_release=self.close_dialog,
                    
                ),
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    font_size=15,
                    height=30,
                    md_bg_color='white',
                    theme_text_color="Custom",
                    font_name=Mtext_bold,
                    on_release=self.close_dialog,
                ),
            ],
        )
        self.dialog.open()
            
    #Пример диалогового окна с кнопками Да и Нет
    def start_dialog_YesNo(self, obj):
        self.dialog=MDDialog(
            md_bg_color=self.dark_green,
            text="[color=#ffffff][font=../MTest/Montserrat-Bold.ttf]Сохранить расчёты?[/font][/color]",
           
            buttons=[
                MDFlatButton(
                    text="ДА",
                    md_bg_color='white',
                    theme_text_color="Custom",
                    font_name=Mtext_bold,
                ),
                MDFlatButton(
                    text="НЕТ",
                    md_bg_color='white',
                    theme_text_color="Custom",
                    font_name=Mtext_bold,
                ),
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    md_bg_color='white',
                    theme_text_color="Custom",
                    font_name=Mtext_bold,
                    on_release=self.close_dialog,
                ),
            ],
        )
        self.dialog.open()
        
    def close_dialog(self, obj):
        self.dialog.dismiss()

    #Window.size = (360, 800)
    ##Задаём настройки экрана - библиотеку ctypes
    def center_window():
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        width, height = Window.size
        Window.left = (screen_width - width) // 2
        Window.top = (screen_height - height) // 8

    Window.size = (340, 760)
    center_window()

    def build(self):
        self.theme_cls.primary_palette = 'BlueGray' #Тема для MDTextField. К сожалению, не разобралась, как поставить свою палитру
        return RootScreen()

if __name__ == "__main__":
    MainApp().run()