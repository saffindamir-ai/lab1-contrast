# -*- coding: utf-8 -*-
"""Unit-тесты для ЛР № 1 (запуск: pipenv run python -m pytest my_tests.py)."""
import io

import numpy as np
import pytest
from PIL import Image

import image_processing as ip


def make_png(color=(200, 100, 50), size=(40, 30)):
    """Создает в памяти PNG-картинку: левая половина цветная, правая черная."""
    arr = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    arr[:, : size[0] // 2] = color
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return buf.getvalue()


# ---------- тесты модуля обработки изображений ----------

def test_level_one_keeps_image():
    img = ip.load_image(make_png())
    assert np.array_equal(ip.change_contrast(img, 1.0), img)


def test_level_zero_gives_gray():
    img = ip.load_image(make_png())
    out = ip.change_contrast(img, 0.0)
    # все пиксели одинаковые (однотонная картинка)
    assert len(np.unique(out.reshape(-1, 3), axis=0)) == 1


def test_contrast_increases_spread():
    img = ip.load_image(make_png((150, 150, 150)))
    low = ip.change_contrast(img, 0.5)
    high = ip.change_contrast(img, 2.0)
    assert low.std() < img.std() < high.std()


def test_values_are_clipped():
    img = ip.load_image(make_png((250, 250, 250)))
    out = ip.change_contrast(img, 3.0)
    assert out.dtype == np.uint8 and out.max() == 255 and out.min() == 0


def test_wrong_level_raises():
    img = ip.load_image(make_png())
    with pytest.raises(ValueError):
        ip.change_contrast(img, 5)


def test_histogram_counts_all_pixels():
    img = ip.load_image(make_png(size=(40, 30)))
    hists = ip.color_histograms(img)
    assert all(len(h) == 256 and h.sum() == 40 * 30 for h in hists.values())


# ---------- тесты веб-приложения ----------

@pytest.fixture
def client():
    from some_app import app
    # TESTING=True: Flask-WTF пропускает проверку капчи в тестах,
    # CSRF отключаем, т.к. тест не получает токен со страницы
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app.test_client()


def test_index_page(client):
    assert client.get("/").status_code == 200


def test_form_page(client):
    r = client.get("/contrast")
    assert r.status_code == 200
    assert "Уровень контраста" in r.get_data(as_text=True)


def test_post_image(client):
    data = {"contrast": "2.0",
            "upload": (io.BytesIO(make_png()), "test.png")}
    r = client.post("/contrast", data=data, content_type="multipart/form-data")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    # на странице три картинки: исходная, результат, графики
    assert html.count("data:image/png;base64,") == 3


def test_post_not_image(client):
    data = {"contrast": "1.0",
            "upload": (io.BytesIO(b"hello"), "text.txt")}
    r = client.post("/contrast", data=data, content_type="multipart/form-data")
    assert "только изображения" in r.get_data(as_text=True)
