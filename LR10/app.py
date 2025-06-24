from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw
import io
import base64
import os

app = Flask(__name__)


app.config['MAX_IMAGE_SIZE'] = 5000
app.config['UPLOAD_FOLDER'] = 'static/images'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def home():
    return "Добро пожаловать в генератор изображений! Посетите /makeimage для создания изображения."


@app.route('/login')
def login():
    return jsonify({"author": "1147241"})  # Замените на ваш логин


@app.route('/makeimage', methods=['GET', 'POST'])
def make_image():
    if request.method == 'POST':
        try:
            width = int(request.form.get('width'))
            height = int(request.form.get('height'))
            text = request.form.get('text', 'Hello World')

            if (width <= 0 or height <= 0 or
                    width > app.config['MAX_IMAGE_SIZE'] or
                    height > app.config['MAX_IMAGE_SIZE']):
                return render_template('makeimage.html',
                                       message="Invalid image size. Maximum size is {}px".format(
                                           app.config['MAX_IMAGE_SIZE']))

            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)


            left, top, right, bottom = draw.textbbox((0, 0), text)
            text_width = right - left
            text_height = bottom - top

            while text_width > width * 0.9 or text_height > height * 0.9:
                img = Image.new('RGB', (width, height), color=(73, 109, 137))
                draw = ImageDraw.Draw(img)
                text = text[:-1] if len(text) > 1 else ''
                if not text:
                    break
                left, top, right, bottom = draw.textbbox((0, 0), text)
                text_width = right - left
                text_height = bottom - top

            text_x = (width - text_width) / 2
            text_y = (height - text_height) / 2
            draw.text((text_x, text_y), text, fill=(255, 255, 0))

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)

            encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            filename = f"image_{width}x{height}_{hash(text)}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(filepath, 'JPEG')

            return render_template('display_image.html',
                                   img_data=encoded_img,
                                   img_url=f"/static/images/{filename}")

        except (ValueError, TypeError):
            return render_template('makeimage.html',
                                   message="Invalid parameters. Please enter valid numbers.")

    return render_template('makeimage.html')


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5001, ssl_context='adhoc', debug=True)

