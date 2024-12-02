from flask import Flask, request, render_template, send_from_directory
import os
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULT_FOLDER'] = 'static/images/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 保存原始图像的副本
        original_path = os.path.join(app.config['RESULT_FOLDER'], f"original_{filename}")
        with Image.open(file_path) as img:
            img.save(original_path)
        
        result_path = process_image(file_path, filename)
        return render_template('result.html', original=f"original_{filename}", result=result_path.split('/')[-1])
    return "Invalid file type", 400

def process_image(file_path, filename):
    img = Image.open(file_path)
    
    # 压缩图片
    img.thumbnail((800, 800))
    
    # 裁剪图片
    if 'crop' in request.form:
        crop_data = request.form['crop'].split(',')
        left, top, right, bottom = map(int, crop_data)
        img = img.crop((left, top, right, bottom))
    
    # 旋转图片
    if 'rotate' in request.form:
        angle = int(request.form['rotate'])
        img = img.rotate(angle)
    
    # 调整亮度和对比度
    if 'brightness' in request.form:
        brightness = float(request.form['brightness'])
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    
    if 'contrast' in request.form:
        contrast = float(request.form['contrast'])
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    
    # 添加半透明水印并居中显示
    if 'watermark' in request.form:
        watermark_text = request.form['watermark']
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        # 使用 textbbox 计算文本的边界框
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        width, height = img.size
        position = ((width - text_width) // 2, (height - text_height) // 2)
        
        # 创建一个透明的水印层
        watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        draw.text(position, watermark_text, fill=(255, 255, 255, 128), font=font)
        
        # 将水印层与原图合并
        img = Image.alpha_composite(img.convert('RGBA'), watermark_layer)
    
    # 将图像转换为 RGB 模式
    img = img.convert('RGB')
    
    # 保存处理后的图片
    result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    img.save(result_path)
    return result_path

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['RESULT_FOLDER']):
        os.makedirs(app.config['RESULT_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)
