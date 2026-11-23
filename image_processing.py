# -*- coding: utf-8 -*-
"""
Модуль обработки изображений для ЛР № 1, вариант 2.

Задача: изменить контраст картинки по указанному значению уровня
контраста и построить графики распределения цветов (гистограммы
каналов R, G, B) исходной и полученной картинки.

Модуль не зависит от Flask, поэтому его функции можно проверять
отдельно unit-тестами (pytest).
"""
import base64
import io

import numpy as np
from PIL import Image

# matplotlib на сервере работает без графического окна,
# поэтому переключаем его на "безоконный" backend Agg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Ограничения на входные данные
MIN_CONTRAST = 0.0      # 0 - полностью серое изображение
MAX_CONTRAST = 3.0      # 3 - контраст увеличен в 3 раза
MAX_SIDE = 1024         # большие картинки уменьшаем для скорости

# Коэффициенты яркости (рекомендация ITU-R BT.601), такие же
# использует Pillow при переводе изображения в оттенки серого
LUMA = np.array([0.299, 0.587, 0.114])


def load_image(file_bytes):
    """Читает байты файла в RGB-массив numpy формы (H, W, 3), тип uint8."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    # уменьшаем слишком большие изображения с сохранением пропорций
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return np.array(img, dtype=np.uint8)


def change_contrast(image, level):
    """
    Изменяет контраст изображения.

    Формула для каждого пикселя и каждого канала:
        new = mean + level * (old - mean),
    где mean - средняя яркость исходного изображения.
    level = 1 - изображение не меняется,
    0 < level < 1 - контраст уменьшается,
    level > 1 - контраст увеличивается,
    level = 0 - изображение становится однотонно-серым.
    Результат обрезается до диапазона [0, 255].
    """
    if not MIN_CONTRAST <= level <= MAX_CONTRAST:
        raise ValueError(
            f"Уровень контраста должен быть от {MIN_CONTRAST} до {MAX_CONTRAST}")
    # переходим к float, чтобы не было переполнения uint8
    img = image.astype(np.float64)
    # средняя яркость по всем пикселям (одно число)
    mean = float((img @ LUMA).mean())
    result = mean + level * (img - mean)
    return np.clip(np.rint(result), 0, 255).astype(np.uint8)


def color_histograms(image):
    """Возвращает словарь {канал: массив из 256 счетчиков} для R, G, B."""
    return {name: np.bincount(image[:, :, i].ravel(), minlength=256)
            for i, name in enumerate(("R", "G", "B"))}


def image_to_base64(image, fmt="PNG"):
    """Кодирует массив изображения в строку base64 для тега <img src=...>."""
    buf = io.BytesIO()
    Image.fromarray(image).save(buf, fmt)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def plot_histograms(original, result):
    """
    Рисует графики распределения цветов исходной и полученной картинки
    (два графика рядом) и возвращает PNG в виде строки base64.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, img, title in ((axes[0], original, "Исходное изображение"),
                           (axes[1], result, "После изменения контраста")):
        hists = color_histograms(img)
        for name, color in (("R", "red"), ("G", "green"), ("B", "blue")):
            ax.plot(np.arange(256), hists[name], color=color, label=name)
            ax.fill_between(np.arange(256), hists[name], color=color, alpha=0.15)
        ax.set_title(title)
        ax.set_xlabel("Значение яркости канала (0-255)")
        ax.set_xlim(0, 255)
        ax.grid(alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Количество пикселей")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90)
    plt.close(fig)  # обязательно закрываем фигуру, чтобы не было утечки памяти
    return base64.b64encode(buf.getvalue()).decode("ascii")
