from datetime import datetime, timedelta
from app.core.utils.logger import logger
import os
import random
import string
from PIL import Image
import zipfile
import pytz
import requests
from urllib.parse import urlparse
from webob.multidict import MultiDict


def print_object_properties(obj):
    """
    打印对象的所有属性和值，过滤掉以 '__' 开头和可调用的属性。

    :param obj: 需要打印属性的对象
    """
    attributes = dir(obj)
    logger.info(f'print_object_properties====>{obj}-{attributes}\n')
    attributes = [attr for attr in attributes if not attr.startswith("__") and not callable(getattr(obj, attr))]
    for k, attr in enumerate(attributes, start=1):
        try:
            value = getattr(obj, attr)
            logger.info(f'print_object_properties_attr====>{k}-{attr}:{value}\n')
        except AttributeError:
            logger.info(f'print_object_properties_attr====>{k}-{attr}:None\n')

def zipdir(path, ziph):
    """
    压缩指定目录下的所有文件和子目录。

    :param path: 需要压缩的目录路径
    :param ziph: zipfile.ZipFile 对象，用于写入压缩文件
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            # 获取相对路径并添加到压缩文件中
            rel_path = os.path.relpath(os.path.join(root, file), path)
            ziph.write(os.path.join(root, file), arcname=rel_path)

def unzip_file(zip_path, output_dir):
    """
    解压缩指定的 ZIP 文件到目标目录。

    :param zip_path: ZIP 文件的路径
    :param output_dir: 解压后的输出目录
    """
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

def download_file(url, save_path):
    """
    下载指定 URL 的文件并保存到本地。

    :param url: 文件的 URL 地址
    :param save_path: 文件保存的目录
    :return: 保存的文件完整路径，下载失败返回 None
    """
    # 解析 URL 获取文件名
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # 完整保存路径
    full_save_path = os.path.join(save_path, filename)

    # 创建保存目录（如果不存在）
    if not os.path.exists(os.path.dirname(full_save_path)):
        os.makedirs(os.path.dirname(full_save_path))

    # 发起 HTTP GET 请求
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # 写入文件
        with open(full_save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logger.info(f"文件已成功下载到 {full_save_path}")
        return full_save_path
    else:
        logger.error(f"下载失败，服务器返回状态码：{response.status_code}")
        return None

def is_image(file_path):
    """
    判断文件是否为图片类型。

    :param file_path: 文件路径
    :return: 如果是图片返回 True，否则返回 False
    """
    try:
        with Image.open(file_path) as img:
            # 验证图像是否可以被PIL打开
            img.verify()  # 验证图像完整性
            return True
    except (IOError, SyntaxError, Exception):
        # 如果无法打开或验证失败，说明不是有效的图像文件
        return False

def get_image_info(image_path):
    """
    获取图片的基本信息。

    :param image_path: 图片文件路径
    :return: PIL.Image 对象，包含图片信息
    """
    with Image.open(image_path) as img:
        return img

def now():
    """
    获取当前时区的当前时间。

    :return: 带时区信息的当前时间对象
    """
    from app.core.config import settings
    timezone = settings.TIMEZONE
    default_timezone = pytz.timezone(timezone)
    return datetime.now(default_timezone)

def mask_password(data: MultiDict):
    """
    将表单数据中的密码字段用 '*' 掩码处理。

    :param data: 表单数据 MultiDict 对象
    :return: 处理后的表单数据
    """
    if 'password' in data:
        data['password'] = '*' * len(data['password'])
    return data

def parse_form_data(form_data):
    """
    解析嵌套的表单数据，将其转换为嵌套的字典结构。

    :param form_data: 表单数据字典
    :return: 解析后的嵌套字典
    """
    result = {}
    for key, value in form_data.items():
        parts = key.split('[')
        current_dict = result
        for part in parts[:-1]:
            part = part.rstrip(']')
            if part not in current_dict:
                current_dict[part] = {}
            current_dict = current_dict[part]
        last_part = parts[-1].rstrip(']')
        if last_part not in current_dict:
            current_dict[last_part] = value
        else:
            if not isinstance(current_dict[last_part], list):
                current_dict[last_part] = [current_dict[last_part]]
            current_dict[last_part].append(value)
    return result

def ip(request):
    """
    获取客户端的 IP 地址。

    :param request: Flask 请求对象
    :return: 客户端 IP 地址字符串
    """
    if 'HTTP_X_FORWARDED_FOR' in request.environ:
        client_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        client_ip = request.environ['REMOTE_ADDR']
    return client_ip

def generate_thumbnail(image_path, base_path, relative_path,size=(128, 128)):
    """
    生成图像的缩略图并保存。

    :param image_path: 原始图像的路径
    :param base_path: 存储缩略图的基础路径
    :param size: 缩略图的尺寸，默认为 (128, 128)
    :return: 缩略图的相对路径
    """
    # 打开原始图像
    img = Image.open(image_path)
    
    # 生成缩略图，保持纵横比
    img.thumbnail(size)

    # 生成缩略图文件名，前缀为 'thumb_'
    thumbnail_filename = 'thumb_' + os.path.basename(image_path)
    
    # 创建存储缩略图的目录，确保与 base_path 一致
    thumbnail_path = os.path.join(base_path, thumbnail_filename)
    
    # 确保目录存在
    os.makedirs(base_path , exist_ok=True)
    
    # 保存缩略图到指定路径
    img.save(thumbnail_path)
    
    # 返回缩略图的相对路径，供外部访问
    return os.path.join(relative_path,thumbnail_filename)

