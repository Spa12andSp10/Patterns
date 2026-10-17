from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor
from PIL import Image, ImageDraw, ImageFont
import io

class png_report(abstract_report):
    """Формирует отчет в виде картинки PNG с нарисованной таблицей."""

    def build(self, source):
        """Рисует таблицу с данными и сохраняет её в PNG.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с бинарными данными (PNG).
        """
        validator.validate(source, object, "source")
        
        header, rows = report_data_extractor.extract(source)
        data = [header] + rows

        row_height = 30
        padding = 10
        font_size = 14
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        num_cols = len(header)
        col_widths = [80] * num_cols

        for row in data:
            for col_idx, cell_text in enumerate(row):
                text_str = str(cell_text)
                estimated_width = len(text_str) * 8 + 20 
                if estimated_width > col_widths[col_idx]:
                    col_widths[col_idx] = estimated_width

        total_width = sum(col_widths) + padding * 2
        total_height = len(data) * row_height + padding * 2

        img = Image.new('RGB', (total_width, total_height), color='white')
        draw = ImageDraw.Draw(img)

        y = padding
        for row in data:
            x = padding
            for col_idx, cell_text in enumerate(row):
                rect = [x, y, x + col_widths[col_idx], y + row_height]
                
                draw.rectangle(rect, outline="black", width=1)
                
                text_y = y + (row_height - font_size) // 2 
                draw.text((x + 5, text_y), str(cell_text), fill="black", font=font)
                
                x += col_widths[col_idx]
            y += row_height
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        result = report_result_dto()
        result.binary = png_bytes
        return result