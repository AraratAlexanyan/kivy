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

    def open_file_chooser(self):
        """Открыть окно выбора файла PDF."""
        if not check_permission(Permission.READ_EXTERNAL_STORAGE ):
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        if not check_permission(Permission.MANAGE_EXTERNAL_STORAGE):
            request_permissions([Permission.MANAGE_EXTERNAL_STORAGE])

        storage_path = primary_external_storage_path()  # Default path
        if not isdir(storage_path):  # Fallback to /sdcard/Download if path is invalid
            storage_path = '/sdcard/Download'

        content = FileChooserListView(path=storage_path)
        content.filters = [lambda folder, filename: filename.endswith('.pdf')]  # Filter only PDF files
        popup = Popup(
            title="Выберите PDF файл",
            content=content,
            size_hint=(0.9, 0.9),
        )

        def on_file_selected(instance, selection, *args):
            if selection:
                self.pdf_path = selection[0]  # Set the PDF file path
                self.status = f"Выбран PDF: {self.pdf_path}"
            popup.dismiss()

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
