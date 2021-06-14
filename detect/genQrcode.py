import qrcode
from PIL import Image

qr = qrcode.QRCode(version = 15, error_correction = qrcode.constants.ERROR_CORRECT_H, box_size = 3,border = 4)
qr.add_data('lion king')
qr.make(fit = True)

img = qr.make_image()
img = img.convert('RGBA')
# 設定色彩
# img = qr.make_image(fill_color="blue")

# 讀取客製化圖片以嵌入QR code中
icon = Image.open('/content/lionKing.jpeg')
img_w, img_h = img.size
factor = 4
size_w = int(img_w/factor)
size_h = int(img_h/factor)

icon_w, icon_h = icon.size
if icon_w > size_w:
	icon_w = size_w
if icon_h > size_h:
	icon_h = size_h

icon = icon.resize((icon_w, icon_h), Image.NEAREST)

w = int((img_w - icon_w)/2)
h = int((img_h - icon_h)/2)
icon = icon.convert('RGBA')
img.paste(icon, (w,h), icon)

img.save("logoQR1.png")
