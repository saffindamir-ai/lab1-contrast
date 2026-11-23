# -*- coding: utf-8 -*-
"""
ЛР № 1 «Разработка веб-приложения на Python», вариант 2.

Веб-приложение на Flask: пользователь загружает картинку, задает
уровень контраста и проходит проверку на робота (Google reCAPTCHA v2).
Приложение показывает исходную и полученную картинки и графики
распределения цветов для обеих.
"""
import os

from flask import Flask, render_template
# модули работы с формами и полями в формах (как в методических указаниях)
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import DecimalRangeField, SubmitField
# модули валидации полей формы
from wtforms.validators import InputRequired, NumberRange

import image_processing as ip

app = Flask(__name__)

# Секретный ключ для защиты форм от CSRF-атак.
# Берем из переменной окружения, если ее нет - генерируем случайный.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24).hex()

# Ключи капчи, полученные в консоли https://www.google.com/recaptcha/admin
# (reCAPTCHA v2, домены localhost, 127.0.0.1 и домен на render.com).
# В коде ключи не храним - только в переменных окружения.
app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get("RECAPTCHA_PUBLIC_KEY", "")
app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get("RECAPTCHA_PRIVATE_KEY", "")
app.config["RECAPTCHA_OPTIONS"] = {"theme": "white"}

# Ограничиваем размер загружаемого файла (5 МБ)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


class ContrastForm(FlaskForm):
    """Форма: файл картинки, уровень контраста, капча, кнопка отправки."""
    # поле загрузки файла, валидатор пропускает только изображения
    upload = FileField("Изображение", validators=[
        FileRequired("Выберите файл"),
        FileAllowed(["jpg", "jpeg", "png", "bmp", "gif"],
                    "Можно загружать только изображения")])
    # ползунок уровня контраста от 0 до 3 с шагом 0.1
    contrast = DecimalRangeField("Уровень контраста", default=1.5, places=1,
                                 validators=[
                                     InputRequired(),
                                     NumberRange(ip.MIN_CONTRAST, ip.MAX_CONTRAST)])
    # поле с капчей
    recaptcha = RecaptchaField()
    submit = SubmitField("Изменить контраст")


@app.route("/")
def hello():
    """Стартовая страница - нужна и для проверки, что сервер запущен."""
    return render_template("hello.html")


@app.route("/contrast", methods=["GET", "POST"])
def contrast():
    """GET - показывает форму, POST - обрабатывает изображение."""
    form = ContrastForm()
    result = None
    error = None
    # validate_on_submit: была отправка формы и все поля, включая
    # CSRF-токен и капчу, прошли проверку
    if form.validate_on_submit():
        level = float(form.contrast.data)
        try:
            original = ip.load_image(form.upload.data.read())
            changed = ip.change_contrast(original, level)
            result = {
                "level": level,
                "original": ip.image_to_base64(original),
                "changed": ip.image_to_base64(changed),
                "plot": ip.plot_histograms(original, changed),
            }
        except Exception:  # поврежденный или нечитаемый файл
            error = "Не удалось прочитать изображение. Попробуйте другой файл."
    return render_template("contrast.html", form=form, result=result, error=error)


@app.errorhandler(413)
def too_large(_):
    """Ответ, если файл больше MAX_CONTENT_LENGTH."""
    return render_template("hello.html",
                           message="Файл слишком большой (максимум 5 МБ)."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
