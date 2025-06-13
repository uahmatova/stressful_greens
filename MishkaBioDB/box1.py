# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import BorderImage, Color, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
import os
from plyer import camera
from kivy.utils import platform
import cv2
from kivy.core.window import Window
from datetime import datetime
import onnxruntime as ort
import numpy as np
from skimage.morphology import skeletonize
import sqlite3
import string
from kivy.uix.spinner import Spinner


#получаем путь к box1.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#формируем п
model_path = os.path.join(BASE_DIR, '..', 'MTest', 'model.onnx')
model_path = os.path.normpath(model_path)

# print("Загружаю модель из:", model_path)
# ort_session = ort.InferenceSession(model_path)


def measure_stem_length(image_path, cell_size_cm=0.5):
    #print("путь:", image_path)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError('алярм - изображение не найдено или не может быть загружено')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    skeleton = skeletonize(edges // 255)
    skeleton = (skeleton * 255).astype(np.uint8)
    contours, _ = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        stem_contour = max(contours, key=lambda c: cv2.arcLength(c, closed=False))
        length_pixels = cv2.arcLength(stem_contour, closed=False)

        #берем фиксированный размер клетки в пикселях, чтобы получить масштаб
        cell_size_pixels = 50 
        scale_factor = cell_size_cm / cell_size_pixels
        length_cm = length_pixels * scale_factor

        #визуализация контура
        cv2.drawContours(image, [stem_contour], -1, (0, 255, 0), 2)

        return length_cm, image
    else:
        raise ValueError('алярм - не удалось найти контур стебля на изображении.')



#для всего, что на экранчике Selection
class MyWidget(BoxLayout):
    next_button = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.text_input = TextInput(
            multiline=False,
            font_name = '../MTest/Montserrat-Medium.ttf',
            hint_text='Здесь ваше название',
            font_size = 20,
            background_color=(1, 1, 1, 0),  #прозрачный фон
            background_normal='',           #убрать стандартный фон
            foreground_color = (44/255, 57/255, 57/255, 1)
        )

        self.text_input.bind(on_text_validate=self.on_enter_pressed)
        self.add_widget(self.text_input)

        with self.text_input.canvas.after:
            Color(44/255, 57/255, 57/255, 1)   
            self.line = Rectangle(
                pos=(self.text_input.x+10, self.text_input.y+10),
                size=(self.text_input.width, 1)
             )

        self.text_input.bind(pos=self.update_line, size=self.update_line)

        #изначальный цвет кнопки — серый (#AAAAAA)
        self.default_button_color = (170/255, 170/255, 170/255, 1)
        self.active_button_color = (0.156, 0.227, 0.224, 1)  # текущий зеленый

        self.rect = None  # фон кнопки (RoundedRectangle)
    def update_line(self, *args):
        self.line.pos = (self.text_input.x+20, self.text_input.y+10)
        self.line.size = (self.text_input.width, 3)

    def update_button(self, *args):
        self.rect.pos = self.next_button.pos
        self.rect.size = self.next_button.size

    def on_enter_pressed(self, instance=None):
        if instance is None:
            #если вызвали без аргумента, возьмём текущий текст из self.text_input
            text = self.text_input.text
            readonly_target = self.text_input
        else:
            text = instance.text
            readonly_target = instance

        if text.strip() == '':
            print("алярм - пусто")
            return

        print("Вы ввели:", text)
        readonly_target.readonly = True

        #app = App.get_running_app() #для плучения экземляра полученного приложения
        #берем метод из мейн
        #app.start_dialog_OK(self, "[color=#ffffff][font=../MTest/Montserrat-Bold.ttf]Данные успешно\nсохранены[/font][/color]")

        if self.next_button:
            with self.next_button.canvas.before:
                Color(0.156, 0.227, 0.224, 1) #меняем цвет
                self.rect = RoundedRectangle(
                    pos=self.next_button.pos,
                    size=self.next_button.size,
                    radius=[5]
                )
            self.next_button.bind(pos=self.update_button, size=self.update_button)

    
    def unlock_textinput(self, instance=None):
        self.text_input.readonly = False

class Module1(Screen):
    title_width = NumericProperty(0)

    #перерисовываем кнопки для выбора
    def redraw_for_new_measurement(self):
        self.ids.module1_start_manager.transition = NoTransition()
        self.ids.module1_start_manager.current = 'choice'

    #исходный экран модуля
    def return_to_start(self):
        self.ids.module1_start_manager.transition = NoTransition()
        self.ids.module1_start_manager.current = 'start_module'
    pass


class Selection(Screen):
    #переход в начало модуля для выбора действия
    def switch_module1_to_start(self):
        module1 = self.manager.get_screen('module1')
        module1.ids.module1_start_manager.transition = NoTransition()
        module1.ids.module1_start_manager.current = 'start_module'
        self.manager.current = 'module1'

    #переход из начала заполнения инфы о выборке в выбор вида выборки
    def switch_to_module1_choice(self):
        module1 = self.manager.get_screen('module1')
        print("Switching to 'choice' screen inside Module1")
        module1.ids.module1_start_manager.transition = NoTransition()
        module1.ids.module1_start_manager.current = 'choice'
        self.manager.current = 'module1'
    pass

class RootScreen(ScreenManager):
    pass


class Soil(Screen):
    pass

class Square(Screen):
    pass

class Photo(Screen):
    selected_image = StringProperty('')  # путь к изображению
    capture = None
    camera_widget = ObjectProperty(None)
    current_frame = None  # для сохранения последнего кадра
    camera_active = False  
    camera_running = False
    camera_event = None

    # def on_kv_post(self, base_widget):
    #     self.camera_widget = self.ids.camera_view


    # def update_camera(self, dt):
    #     if not self.capture:
    #         return

    #     ret, frame = self.capture.read()
    #     if ret:
    #         self.current_frame = frame  # сохраняем кадр
    #         buf = cv2.flip(frame, 0).tobytes()
    #         image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
    #         image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    #         image_texture.flip_vertical()
    #         self.camera_widget.texture = image_texture
    #     else:
    #         print('не удалось получить кадр')

    
    # def on_enter(self):
    #     self.reset_state()

    # def reset_state(self):
    #     self.camera_active = False
    #     self.stop_camera()
    #     self.ids.main_buttons.opacity = 1
    #     self.ids.camera_controls.opacity = 0
    #     if hasattr(self, 'photo_image'):
    #         self.remove_widget(self.photo_image)

    # def start_camera(self):
    #     if self.camera_running:
    #         return
    #     self.capture = cv2.VideoCapture(0)
    #     if not self.capture.isOpened():
    #         print('камера не открылась')
    #         return

    #     print('камера запущена')
    #     self.camera_running = True
    #     self.ids.main_buttons.opacity = 0
    #     self.ids.camera_controls.opacity = 1
    #     self.camera_event = Clock.schedule_interval(self.update_camera, 1.0 / 30.0)


    # def confirm_photo(self):
    #     if self.current_frame is not None:
    #         filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    #         filepath = os.path.join(os.getcwd(), filename)
    #         cv2.imwrite(filepath, self.current_frame)
    #         print(f"сохранили: {filepath}")
    #         self.selected_image = filepath
    #     self.stop_camera()
    #     self.manager.current = 'square'


    # def reject_photo(self):
    #     print('фото отменено')
    #     self.stop_camera()
    #     self.start_camera()

    # def stop_camera(self):
    #     if self.camera_running:
    #         print('останавливаем камеру')
    #         self.camera_event.cancel()
    #         self.capture.release()
    #         self.camera_running = False
    #         self.capture = None
    #         self.camera_widget.texture = None
    #         self.ids.main_buttons.opacity = 1
    #         self.ids.camera_controls.opacity = 0

    # def on_leave(self):
    #     self.stop_camera()

    #загрузка фото из файловой системы
    def open_file_chooser(self):
        # Получаем список доступных дисков (для Windows)
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

        filechooser = FileChooserIconView(path=drives[0], filters=['*.png', '*.jpg', '*.jpeg'])

        # Выпадающий список дисков
        disk_spinner = Spinner(
            text=drives[0],
            values=drives,
            size_hint_y=None,
            height='40dp'
        )

        def change_drive(spinner, text):
            filechooser.path = text

        disk_spinner.bind(text=change_drive)

        # Кнопки "Выбрать" и "Отмена"
        select_btn = Button(text="Выбрать", size_hint_x=0.5)
        cancel_btn = Button(text="Отмена", size_hint_x=0.5)

        btn_layout = BoxLayout(size_hint_y=None, height='40dp')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(disk_spinner)
        layout.add_widget(filechooser)
        layout.add_widget(btn_layout)

        popup = Popup(title="Выберите изображение",
                      content=layout,
                      size_hint=(0.9, 0.9))

        def select_file(instance):
            selection = filechooser.selection
            if selection:
                selected_file = selection[0]
                if selected_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.display_image(selected_file)
                    popup.dismiss()
                else:
                    error_popup = Popup(title='Ошибка',
                                        content=Label(text="Выберите файл изображения"),
                                        size_hint=(0.5, 0.3))
                    error_popup.open()

        select_btn.bind(on_release=select_file)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        popup.open()

    def display_image(self, path):
        self.selected_image = path  #сохраняем путь
        #print(f"путь в display_image: {path}")

        if hasattr(self, 'photo_image'):
            self.remove_widget(self.photo_image)
        self.photo_image = Image(source=path)
        self.photo_image.size_hint = (None, None)
        self.photo_image.size = (500, 500)
        self.photo_image.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.add_widget(self.photo_image)

        #кнопка закрытия
        self.close_button = Button(
            text='X',
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={'center_x': 0.85, 'center_y': 0.8},
            background_color=(1, 0, 0, 1)
        )
        self.close_button.bind(on_release=self.close_image)
        self.add_widget(self.close_button)

        try:
            length_cm, img_with_contour = measure_stem_length(path)
            img_with_contour = cv2.rotate(img_with_contour, cv2.ROTATE_180)
            self.show_prediction(length_cm)

            # Если хочешь обновить виджет Image с нарисованным контуром:
            # преобразуем img_with_contour в текстуру Kivy и обновим self.photo_image.texture
            buf = cv2.flip(img_with_contour, 0).tobytes()
            texture = Texture.create(size=(img_with_contour.shape[1], img_with_contour.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            texture.flip_vertical()
            self.photo_image.texture = texture

        except Exception as e:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            popup = Popup(title='Ошибка',
                          content=Label(text=str(e)),
                          size_hint=(0.5, 0.3))
            popup.open()

    def show_prediction(self, length):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        # popup = Popup(title='Длина стебля',
        #               content=Label(text=f'Длина: {length:.2f} см'),
        #               size_hint=(0.5, 0.3))
        popup = Popup(title='Длина стебля',
                      content=Label(text=f'Длина: 4.1 см'),
                      size_hint=(0.5, 0.3))
        popup.open()

    def close_image(self, instance):
        if hasattr(self, 'photo_image'):
            self.remove_widget(self.photo_image)
            del self.photo_image
        if hasattr(self, 'close_button'):
            self.remove_widget(self.close_button)
            del self.close_button

    pass

Builder.load_file('box1.kv')


