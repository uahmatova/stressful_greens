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
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BooleanProperty
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
from db import get_connection
from collections import Counter
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock


#подключаемся к бд
get_connection()

#получаем путь к box1.py
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# #формируем п
# model_path = os.path.join(BASE_DIR, '..', 'MTest', 'model.onnx')
# model_path = os.path.normpath(model_path)

# print("Загружаю модель из:", model_path)
# ort_session = ort.InferenceSession(model_path)

#функция определения клетки на фото
def calculate_scale_from_grid_like_human(image_crop, cell_size_cm=0.5):
    # print("исходное изображение:")
    # cv2_imshow(image_crop)

    # Градации серого + усиление контраста
    gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    inverted = cv2.bitwise_not(enhanced)

    # Адаптивный порог + морфология
    thresh = cv2.adaptiveThreshold(inverted, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY, 15, -10)
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # print("обработанное изображение для линий:")
    # cv2_imshow(closed)

    edges = cv2.Canny(closed, 50, 150)
    #преобразование Хафа — ищем прямые линии
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=40, maxLineGap=20)

    if lines is None:
        raise ValueError("линии не найдены")

    # Разделение на вертикальные и горизонтальные
    verticals = []
    horizontals = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        angle = np.arctan2(dy, dx) * 180 / np.pi
        if abs(angle) < 10:
            horizontals.append((y1 + y2) // 2)
        elif abs(angle - 90) < 10 or abs(angle + 90) < 10:
            verticals.append((x1 + x2) // 2)

    #удаляем дубли — округлим и сгруппируем
    def dedup(lines, delta=10):
        lines = sorted(lines)
        clustered = []
        cluster = [lines[0]]
        for val in lines[1:]:
            if abs(val - cluster[-1]) < delta:
                cluster.append(val)
            else:
                clustered.append(int(np.mean(cluster)))
                cluster = [val]
        clustered.append(int(np.mean(cluster)))
        return clustered

    v_lines = dedup(verticals)
    h_lines = dedup(horizontals)

    print(f"горизонтальных линий (уникальных): {len(h_lines)}")
    print(f"вертикальных линий (уникальных): {len(v_lines)}")

    if len(v_lines) < 2 or len(h_lines) < 2:
        raise ValueError("недостаточно линий для клетки")

    def find_dominant_spacing(lines):
        spacings = [lines[i+1] - lines[i] for i in range(len(lines)-1)]
        rounded = [int(round(s / 5.0) * 5) for s in spacings]  # округляем для устойчивости
        most_common = Counter(rounded).most_common(1)[0][0]
        for i in range(len(spacings)):
            if abs(spacings[i] - most_common) <= 5:
                return lines[i], lines[i+1]
        raise ValueError("не удалось определить клетку.")
    
    x1, x2 = find_dominant_spacing(v_lines)
    y1, y2 = find_dominant_spacing(h_lines)


    #найденная клетка
    img_with_cell = image_crop.copy()
    cv2.rectangle(img_with_cell, (x1, y1), (x2, y2), (0, 0, 255), 2)
    # print("найденная клетка:")
    # cv2_imshow(img_with_cell)

    #расчёт масштаба
    cell_px = max(abs(x2 - x1), abs(y2 - y1))
    scale = cell_size_cm / cell_px
    print(f"Размер клетки: {cell_px:.1f}px ≈ {cell_size_cm} см")
    print(f"Масштаб: {scale:.5f} см/пиксель")

    return scale


#функция определения длины стебля по найденному масштабу
def measure_stem_length(image_path, scale_factor):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError('Изображение не найдено')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    #скелетизация
    skeleton = skeletonize(edges // 255)
    skeleton = (skeleton * 255).astype(np.uint8)

    stem_contours, _ = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not stem_contours:
        raise ValueError("Контур стебля не найден")

    stem_contour = max(stem_contours, key=lambda c: cv2.arcLength(c, False))
    length_pixels = cv2.arcLength(stem_contour, False)
    length_cm = length_pixels * scale_factor
    length_cm = length_cm/1.37

    cv2.drawContours(image, [stem_contour], -1, (0, 255, 0), 2)
    text = f"Длина стебля: {length_cm:.2f} см"
    cv2.putText(image, text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # cv2.imshow(image)
    return length_cm, image



#для всего, что на экранчике Selection
class MyWidget(BoxLayout):
    next_button = ObjectProperty()
    show_dropdown = BooleanProperty(False)

    def __init__(self, **kwargs):
        show_dropdown = kwargs.pop('show_dropdown', False)
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.show_dropdown = show_dropdown

        self.text_input = TextInput(
            multiline=False,
            font_name='../MTest/Montserrat-Medium.ttf',
            hint_text='Здесь ваше название',
            font_size=20,
            background_color=(1, 1, 1, 0),  # прозрачный фон
            background_normal='',           # убрать стандартный фон
            foreground_color=(44/255, 57/255, 57/255, 1)
        )
        self.text_input.bind(on_text_validate=self.on_enter_pressed)
        #self.add_widget(self.text_input)

        # Линия под TextInput
        with self.text_input.canvas.after:
            Color(44/255, 57/255, 57/255, 1)
            self.line = Rectangle(
                pos=(self.text_input.x + 10, self.text_input.y + 10),
                size=(self.text_input.width, 1)
            )
        self.text_input.bind(pos=self.update_line, size=self.update_line)

        if show_dropdown:
            # Создаем кнопку рядом с текстовым полем для показа выпадающего списка
            self.dropdown_button = Button(text='▼', size_hint=(None, None), size=(30, self.text_input.height))
            self.dropdown_button.bind(on_release=self.open_dropdown)

            # Поместим кнопку и текстовое поле в горизонтальный BoxLayout
            self.input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=self.text_input.height)
            self.input_layout.add_widget(self.text_input)
            self.input_layout.add_widget(self.dropdown_button)

            self.clear_widgets()
            self.add_widget(self.input_layout)

            self.dropdown = DropDown()
        else:
            # Просто добавляем текстовое поле, без кнопки и дропдауна
            self.add_widget(self.text_input)
            self.dropdown = None


    def fill_dropdown_from_db(self):
        if not self.dropdown:
            return  # Если дропдаун не создан, просто выходим
        # Подключаемся к БД и получаем список значений из Soil (без id)
        conn = sqlite3.connect('stressfull_greens.db')
        cursor = conn.cursor()
        cursor.execute("SELECT soil_value FROM Soil")
        soils = cursor.fetchall()
        conn.close()

        self.dropdown.clear_widgets()
        for (soil_value,) in soils:
            btn = Button(text=soil_value, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_item(btn.text))
            self.dropdown.add_widget(btn)

    def select_item(self, text):
        self.text_input.text = text
        self.dropdown.dismiss()

    def open_dropdown(self, instance):
        self.dropdown.open(instance)



    def update_line(self, *args):
        self.line.pos = (0, self.text_input.y+10)
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
    def show_view_choice(self):
        self.ids.module1_start_manager.current = 'view_choice'

    def return_to_start(self):
        self.ids.module1_start_manager.current = 'start_module'

    def show_results(self, result_type):
        # Сохрани флаг типа результата
        App.get_running_app().result_type = result_type

        # Переход на экран с таблицей (предположим, 'results_screen')
        self.ids.module1_start_manager.current = 'results_screen'

        # Вызов функции для загрузки данных
        self.load_results_from_db(result_type)

    def load_results_from_db(self, result_type):
        conn = get_connection()
        cursor = conn.cursor()

        if result_type == "test":
            cursor.execute("SELECT * FROM Test_control")
        else:
            cursor.execute("SELECT * FROM Selection")

        data = cursor.fetchall()
        conn.close()
    def load_results_from_db(self, result_type):
        conn = get_connection()
        cursor = conn.cursor()

        if result_type == "test":
            cursor.execute("SELECT * FROM Test_control")
        else:
            cursor.execute("SELECT * FROM Selection")

        data = cursor.fetchall()
        conn.close()

        results_table = self.ids.results_table
        results_table.clear_widgets()

        for row in data:
            for cell in row:
                results_table.add_widget(Label(
                    text=str(cell),
                    font_size='16sp',
                    color=(0.156, 0.227, 0.224, 1)
                ))

    

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
    def get_soil_values(self):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT soil_value FROM Soil")
            soils = [row[0] for row in cursor.fetchall()]
            soils.append("Другое...")   # Добавляем вариант для ручного ввода
            conn.close()
            return soils
    def on_enter(self):
        self.ids.soil_spinner.values = self.get_soil_values()

    def update_button(self, instance, value):
        if hasattr(self, 'next_rect'):
            self.next_rect.pos = instance.pos
            self.next_rect.size = instance.size


    def on_spinner_select(self, spinner, text):
        if text == "Другое...":
            self.open_manual_input()
        elif text != "Выберите почву":
            # Разблокируем кнопку "далее"
            btn = self.ids.next_button
            btn.disabled = False

            if not hasattr(self, 'next_rect'):
                with btn.canvas.before:
                    Color(0.156, 0.227, 0.224, 1)  # Тёмно-зелёный фон
                    self.next_rect = RoundedRectangle(
                        pos=btn.pos,
                        size=btn.size,
                        radius=[5]
                    )
            # Обновим позицию/размер на всякий случай
            btn.bind(pos=self.update_button, size=self.update_button)


    def open_manual_input(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ti = TextInput(hint_text="Введите название почвы", multiline=False, size_hint_y=None, height=40)
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        ok = Button(text="ОК")
        cancel = Button(text="Отмена")
        btn_layout.add_widget(ok)
        btn_layout.add_widget(cancel)
        content.add_widget(ti)
        content.add_widget(btn_layout)

        popup = Popup(title="Другая почва", content=content,
                      size_hint=(None, None), size=(300, 200), auto_dismiss=False)

        def do_ok(instance):
            val = ti.text.strip()
            if val:
                # подставляем введённое значение
                self.ids.soil_spinner.text = val
                # при желании: добавить в базу
                conn = get_connection()
                c = conn.cursor()
                c.execute("INSERT INTO Soil (soil_value) VALUES (?)", (val,))
                conn.commit()
                conn.close()

                btn = self.ids.next_button
                btn.disabled = False

                if not hasattr(self, 'next_rect'):
                    with btn.canvas.before:
                        Color(0.156, 0.227, 0.224, 1)
                        self.next_rect = RoundedRectangle(
                            pos=btn.pos,
                            size=btn.size,
                            radius=[5]
                        )

            popup.dismiss()

        def do_cancel(instance):
            # сбросим выбор назад на первый элемент
            self.ids.soil_spinner.text = "Выберите почву"
            popup.dismiss()

        ok.bind(on_release=do_ok)
        cancel.bind(on_release=do_cancel)
        popup.open()
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
            image = cv2.imread(path)
            grid_crop = image[50:500, 100:600]  #[y1:y2, x1:x2]
            scale = calculate_scale_from_grid_like_human(grid_crop)

     
            length_cm, img_with_contour = measure_stem_length(path, scale)
            img_with_contour = cv2.rotate(img_with_contour, cv2.ROTATE_180)
            self.show_prediction(length_cm)

            # Преобразуем изображение в текстуру для отображения в интерфейсе
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
        popup = Popup(title='Длина стебля',
                      content=Label(text=f'Длина: {length:.2f} см'),
                      size_hint=(0.5, 0.3))
        # popup = Popup(title='Длина стебля',
        #               content=Label(text=f'Длина: 4.1 см'),
        #               size_hint=(0.5, 0.3))
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


