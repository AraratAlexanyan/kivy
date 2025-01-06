import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty
from pdf2image import convert_from_path
from printer_logic import process_and_print  # Импорт вашей логики печати

class PrinterAppWidget(BoxLayout):
    status = StringProperty("Выберите параметры и нажмите 'Печать'.")
    pdf_path = StringProperty("")  # Путь к PDF файлу

    def open_file_chooser(self):
        """Открыть окно выбора файла PDF."""
        content = FileChooserListView()
        content.filters = ['*.pdf']  # Фильтрация только по PDF
        popup = Popup(
            title="Выберите PDF файл",
            content=content,
            size_hint=(0.9, 0.9),
        )

        # Функция срабатывает при выборе файла
        def on_file_selected(instance, selection, *args):
            if selection:
                self.pdf_path = selection[0]  # Устанавливаем путь к PDF файлу
                self.status = f"Выбран PDF: {self.pdf_path}"
            popup.dismiss()

        content.bind(on_submit=on_file_selected)
        popup.open()

    def print_pdf(self):
        try:
            if not self.pdf_path:
                raise ValueError("Выберите PDF для печати!")

            # Преобразуем PDF в изображения
            images = convert_from_path(self.pdf_path)

            # Убедимся, что директория 'output' существует
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Сбор данных из интерфейса
            model = self.ids.model_spinner.text
            conn = self.ids.conn_spinner.text
            addr = self.ids.addr_input.text
            density = int(self.ids.density_spinner.text)
            rotate = self.ids.rotate_spinner.text
            verbose = self.ids.verbose_checkbox.active
            image_paths= []


            for idx, image in enumerate(images):

                image_path = os.path.join(output_dir, f"page_{idx + 1}.png")
                image_paths.append(image_path)
                image.save(image_path, "PNG")


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
