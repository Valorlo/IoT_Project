import qrcode
import numpy as np
import pyzbar.pyzbar as zbar
import cv2
import matplotlib.pyplot as plt

qr = qrcode.QRCode(version = 15, error_correction = qrcode.constants.ERROR_CORRECT_H, box_size = 3,border = 4) #1~40的整數
qr.add_data('hello') # QRCode資訊
qr.make(fit = True)

img = qr.make_image()
img.save("./QRcodehello.png") # 儲存圖片
