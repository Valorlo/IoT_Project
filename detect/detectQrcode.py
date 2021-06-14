import qrcode
import numpy as np
import pyzbar.pyzbar as zbar
import cv2
import matplotlib.pyplot as plt

def detect(I): 
    # 偵測所有的 QR code
    barcodes = zbar.decode(I)
    
    # 逐一解碼，回傳位置與結果
    bbox = []; msg = [];
    for i, barcode in enumerate(barcodes):
        bbox.append(np.array(barcode.rect))
        msg.append(barcode.data.decode('utf-8'))

    return bbox, msg 

def decided_yaw(x,y):
    imW = 1280
    imH = 720
    xleft = 1/3
    xright = 2/3
    ylow = 1/3
    yhigh = 2/3
    if x<=(imW * xleft):
        if y<=(imH * ylow):
            result  = "area1"
            # print("1")
            return result
        elif y>(imH *ylow) and y<=(imH * yhigh):
            result  = "area4"
            # print("4")
            return result
        elif y>(imH * yhigh):
            result  = "area7"
            # print("7")
            return result

    elif x>(imW * xleft) and x<=(imW * xright):
        if y<=(imH * ylow):
            result  = "area2"
            # print("2")
            return result
        elif y>(imH * ylow) and y<=(imH*yhigh):
            result  = "area5"
            # print("5")
            return result
        elif y>(imH*yhigh):
            result  = "area8"
            # print("8")
            return result

    elif x>(imW*xright):
        if y<=(imH * ylow):
            result  = "area3"
            # print("3")
            return result
        elif y>(imH * ylow) and y<=(imH*yhigh):
            result  = "area6"
            # print("6")
            return result
        elif y>(imH*yhigh):
            result  = "area9"
            # print("9")
            return result

def detect_human(img_path):
  I = cv2.imread(img_path)

  wherex = 0
  wherey = 0
  whereW = 0
  whereH = 0
  result = 'None'
  find_msg = 'lion king'
  bbox, msg = detect(I)
  # print(len(bbox))
  for i in range(len(bbox)):
    c, r, w, h = bbox[i]
    cv2.rectangle(I, (c, r), (c+w, r+h), (0, 255, 0), 5)
    if msg[i] == find_msg:
      wherex = c
      wherey = r
      whereW = w
      whereH = h
    # print(msg[i])
    # print(c, r, w, h)

  print(wherex, wherey, whereW, whereH)

  if wherex!=0 and wherey!=0:
    result = decided_yaw(wherex+whereW/2, wherey+whereH/2)#中心（寬,高）
    print("in")

  return result
  





