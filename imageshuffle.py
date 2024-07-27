import hashlib
import random
from flask import Flask, request, render_template_string, jsonify
from PIL import Image
import io
import base64

app = Flask(__name__)

def generate_short_hash(input_string):
    sha256 = hashlib.sha256(input_string.encode()).hexdigest()
    short_hash = sha256[:16]
    return short_hash

def shuffle_image(image, seed_string):
    short_hash = generate_short_hash(seed_string)
    seed = int(short_hash, 32)
    pixels = list(image.getdata())
    random.seed(seed)
    random.shuffle(pixels)
    shuffled_img = Image.new(image.mode, image.size)
    shuffled_img.putdata(pixels)
    return shuffled_img

def unshuffle_image(image, seed_string):
    short_hash = generate_short_hash(seed_string)
    seed = int(short_hash, 32)
    pixels = list(image.getdata())
    random.seed(seed)
    index_list = list(range(len(pixels)))
    random.shuffle(index_list)
    restored_pixels = [None] * len(pixels)
    for i, index in enumerate(index_list):
        restored_pixels[index] = pixels[i]
    restored_img = Image.new(image.mode, image.size)
    restored_img.putdata(restored_pixels)
    return restored_img

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>简单图像混淆</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
            background: #f4f4f9;
        }
        h1 {
            color: #333;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        img {
            max-width: 100%;
            height: auto;
            margin-bottom: 20px;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .dropzone {
            width: 100%;
            height: 200px;
            border: 2px dashed #007bff;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #007bff;
            cursor: pointer;
            margin-bottom: 20px;
            transition: background-color 0.3s ease;
        }
        .dropzone.hover {
            background-color: #e9ecef;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }
        input[type="text"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background: #0056b3;
        }
        hr {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>简单图像混淆</h1>
        <div class="dropzone" id="dropzone">拖拽或点击以上传图片</div>
        <input type="file" id="fileInput" style="display: none;">
        <img id="preview" src="" alt="请先上传待处理图片">
        <form id="shuffleForm" style="display: none;" enctype="multipart/form-data">
            <h2>Shuffle Image</h2>
            <label for="shuffle_string">请输入加密密钥:</label>
            <input type="text" name="input_string" id="shuffle_string" required>
            <button type="submit">加密图片</button>
        </form>
        <hr>
        <form id="unshuffleForm" style="display: none;" enctype="multipart/form-data">
            <h2>Unshuffle Image</h2>
            <label for="unshuffle_string">请输入解密密钥:</label>
            <input type="text" name="input_string" id="unshuffle_string" required>
            <button type="submit">解密图片</button>
        </form>
        <hr>
        <h2>Output Image</h2>
        <img id="output_image" src="" alt="请等待结果输出">
    </div>
    <script>
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const shuffleForm = document.getElementById('shuffleForm');
        const unshuffleForm = document.getElementById('unshuffleForm');
        let uploadedFile;

        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (event) => {
            event.preventDefault();
            dropzone.classList.add('hover');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('hover'));
        dropzone.addEventListener('drop', (event) => {
            event.preventDefault();
            dropzone.classList.remove('hover');
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (event) => {
            const files = event.target.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        function handleFile(file) {
            uploadedFile = file;
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.src = event.target.result;
                preview.style.display = 'block';
                shuffleForm.style.display = 'block';
                unshuffleForm.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }

        shuffleForm.onsubmit = async function(event) {
            event.preventDefault();
            let formData = new FormData();
            formData.append('image', uploadedFile);
            formData.append('input_string', document.getElementById('shuffle_string').value);
            let response = await fetch('/shuffle', {
                method: 'POST',
                body: formData
            });
            let result = await response.json();
            document.getElementById('output_image').src = result.image_data;
        };

        unshuffleForm.onsubmit = async function(event) {
            event.preventDefault();
            let formData = new FormData();
            formData.append('image', uploadedFile);
            formData.append('input_string', document.getElementById('unshuffle_string').value);
            let response = await fetch('/unshuffle', {
                method: 'POST',
                body: formData
            });
            let result = await response.json();
            document.getElementById('output_image').src = result.image_data;
        };
    </script>
</body>
</html>
''')

@app.route('/shuffle', methods=['POST'])
def shuffle():
    file = request.files['image']
    input_string = request.form['input_string']
    image = Image.open(file.stream)
    shuffled_image = shuffle_image(image, input_string)
    img_io = io.BytesIO()
    shuffled_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return jsonify({'image_data': 'data:image/png;base64,' + img_base64})

@app.route('/unshuffle', methods=['POST'])
def unshuffle():
    file = request.files['image']
    input_string = request.form['input_string']
    image = Image.open(file.stream)
    restored_image = unshuffle_image(image, input_string)
    img_io = io.BytesIO()
    restored_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return jsonify({'image_data': 'data:image/png;base64,' + img_base64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6996)
