import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty
from pdf2image import convert_from_path
from printer_logic import process_and_print  # Импорт вашей логики печати
from android.permissions import request_permissions, Permission, check_permission
from android.storage import primary_external_storage_path
from os.path import isdir

class PrinterAppWidget(BoxLayout):
    status = StringProperty("Выберите параметры и нажмите 'Печать'.")
    pdf_path = StringProperty("")  # Путь к PDF файлу

    def open_file_chooser(self, allowed_extensions=None):
        """Открыть окно выбора файла без фильтров."""
        # Проверка и запрос разрешений
        if not check_permission(Permission.READ_EXTERNAL_STORAGE):
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        if not check_permission(Permission.MANAGE_EXTERNAL_STORAGE):
            request_permissions([Permission.MANAGE_EXTERNAL_STORAGE])

        # Установка пути к хранилищу
        storage_path = primary_external_storage_path()  # Путь к внешнему хранилищу
        if not isdir(storage_path):  # Если путь недоступен, используем стандартный Download
            storage_path = '/sdcard/Download'

        # Создание FileChooser без фильтров
        content = FileChooserListView(
            path=storage_path,
            show_hidden=False,
            filters=allowed_extensions
            # Скрыть скрытые файлы
        )
        popup = Popup(
            title="Выберите файл",
            content=content,
            size_hint=(0.9, 0.9),
        )

        def on_file_selected(instance, selection, *args):
            """Обработчик выбора файла."""
            if selection:
                self.file_path = selection[0]  # Устанавливаем путь к выбранному файлу
                self.status = f"Выбран файл: {self.file_path}"
            popup.dismiss()

        # Привязка события на выбор файла
        content.bind(on_submit=on_file_selected)
        popup.open()

    def print_pdf(self):
        try:
            if not self.pdf_path:
                raise ValueError("Выберите PDF для печати!")

            # Convert PDF to images
            images = convert_from_path(self.pdf_path)

            # Ensure 'output' directory exists
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Collect data from the interface
            model = self.ids.model_spinner.text
            conn = self.ids.conn_spinner.text
            addr = self.ids.addr_input.text
            density = int(self.ids.density_spinner.text)
            rotate = self.ids.rotate_spinner.text
            verbose = self.ids.verbose_checkbox.active
            image_paths = []

            # Save PDF pages as images
            for idx, image in enumerate(images):
                image_path = os.path.join(output_dir, f"page_{idx + 1}.png")
                image_paths.append(image_path)
                image.save(image_path, "PNG")

            # Process and print each image
            for p in image_paths:
                process_and_print(model, conn, addr, density, rotate, p, verbose)

            self.status = "Печать завершена успешно!"

        except Exception as e:
            self.status = f"Ошибка: {e}"


class PrinterApp(App):
    def build(self):
        return PrinterAppWidget()


if __name__ == "__main__":
    PrinterApp().run()
