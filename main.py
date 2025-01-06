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
from android import activity
from jnius import autoclass
from plyer import filechooser

import os

class PrinterAppWidget(BoxLayout):
    status = StringProperty("Выберите параметры и нажмите 'Печать'.")
    pdf_path = StringProperty("")  # Path to the PDF file

   def open_file_chooser(self):
        """Open a file chooser to select a PDF."""
        if not check_permission(Permission.READ_EXTERNAL_STORAGE):
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        # Use Plyer's filechooser to open a file dialog
        try:
            file_path = filechooser.open_file()
            if file_path:
                self.pdf_path = file_path[0]
                self.status = f"Выбран файл: {self.pdf_path}"
            else:
                self.status = "Файл не выбран."
        except Exception as e:
            self.status = f"Ошибка при выборе файла: {e}"

    def get_real_path_from_uri(self, uri):
        """Get the real file path from a URI."""
        DocumentsContract = autoclass('android.provider.DocumentsContract')
        context = autoclass('android.content.Context')
        content_resolver = context.getContentResolver()

        doc_id = DocumentsContract.getDocumentId(uri)
        split = doc_id.split(':')
        file_id = split[1]

        # Build the URI for the document
        base_uri = DocumentsContract.buildDocumentUriUsingTree(uri, file_id)
        cursor = content_resolver.query(base_uri, None, None, None, None)
        if cursor and cursor.moveToFirst():
            column_index = cursor.getColumnIndex("_data")
            path = cursor.getString(column_index)
            cursor.close()
            return path
        return None

    def print_pdf(self):
        """Convert PDF to images and print them."""
        try:
            if not self.pdf_path:
                raise ValueError("Выберите PDF для печати!")

            # Convert PDF to images
            images = convert_from_path(self.pdf_path)

            # Ensure output directory exists
            output_dir = primary_external_storage_path() + "/MyAppOutput"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Collect data from UI
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
