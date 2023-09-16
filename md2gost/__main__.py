#!/bin/python
from argparse import ArgumentParser, BooleanOptionalAction
import os.path
import sys
from getpass import getuser

from md2gost.parser import ParserFactory
from .converter import Converter


def main():
    parser = ArgumentParser(
        prog="md2gost",
        description="Этот скрипт предназначен для генерирования отчетов/\
                курсовых работ по ГОСТ в формате docx из Markdown-файла."
    )
    parser.add_argument("filenames", nargs="*",
                        help="Путь до исходного(-ых) markdown файла(-ов)")
    parser.add_argument("-o", "--output", help="Путь до сгенерированного \
                            файла")
    parser.add_argument("-t", "--template", help="Путь до шаблона .docx")
    parser.add_argument("-T", "--title", help="Путь до файла титульной(-ых) \
                            страниц(ы) в формете docx")
    parser.add_argument("--title-pages", help="Количество страниц в файле титульной(-ых) \
                            страниц(ы) в формете docx", default=1, type=int)
    parser.add_argument("--syntax-highlighting", help="Подсветка синтаксиса в листингах",
                        action=BooleanOptionalAction)
    parser.add_argument("--debug", help="Добавляет отладочные данные в документ",
                        action="store_true")

    args = parser.parse_args()
    filenames, output, template, title, title_pages, debug = \
        args.filenames, args.output, args.template, args.title, args.title_pages, args.debug
    if args.syntax_highlighting:
        os.environ["SYNTAX_HIGHLIGHTING"] = "1"

    if not filenames:
        print("Нет входных файлов!")
        return -1

    if output:
        if not output.endswith(".docx"):
            print("Ошибка: выходной файл должен иметь расширение .docx")
            return -1
    else:
        output = os.path.basename(filenames[0]).replace(".md", ".docx")

    if not template:
        template = os.path.join(os.path.dirname(__file__), "Template.docx")

    converter = Converter(filenames, output, template, title, title_pages, debug)
    converter.convert()

    document = converter.document

    document.core_properties.author = getuser()
    document.core_properties.comments =\
        "Создано при помощи https://github.com/witelokk/md2gost"

    document.save(output)
    print(f"Сгенерированный документ: {os.path.abspath(output)}")

    if debug:
        import platform
        if platform.system() == 'Darwin':       # macOS
            import subprocess
            subprocess.call(('open', output))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(output)
        else:                                   # linux variants
            import subprocess
            subprocess.call(('xdg-open', output))


if __name__ == "__main__":
    sys.exit(main())
