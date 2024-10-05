import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile


# Асинхронна функція для рекурсивного читання файлів у вихідній папці та її підпапках
async def read_folder(path: AsyncPath) -> None:
    async for item in path.iterdir():
        if await item.is_dir():
            # Якщо це директорія, рекурсивно викликаємо функцію для її обробки
            await read_folder(item)
        elif await item.is_file():
            # Якщо це файл, копіюємо його у відповідну папку
            await copy_file(item)


# Асинхронна функція для копіювання файлів у відповідну папку на основі їх розширення
async def copy_file(file: AsyncPath) -> None:
    extension_name = file.suffix[1:]  # Отримуємо розширення файлу (без крапки)
    extension_folder = output / extension_name

    try:
        # Створюємо папку для файлів з таким розширенням, якщо вона не існує
        await extension_folder.mkdir(exist_ok=True, parents=True)
        # Копіюємо файл у відповідну папку
        await copyfile(file, extension_folder / file.name)
        logging.info(f"Copied {file} to {extension_folder / file.name}")
    except Exception as e:
        logging.error(f"Error copying {file}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    # TODO Створити об'єкт ArgumentParser для обробки аргументів командного рядка
    parser = argparse.ArgumentParser(description="Async file sorter based on file extensions.")
    parser.add_argument("--source", type=str, required=True, help="Source folder to read files from.")
    parser.add_argument("--output", type=str, required=True, help="Output folder to sort files into.")
    args = parser.parse_args()

    # Ініціалізуємо шляхи для вихідної та цільової папок
    source = AsyncPath(args.source)
    output = AsyncPath(args.output)

    # Запускаємо асинхронну функцію для обробки файлів у вихідній папці
    asyncio.run(read_folder(source))
