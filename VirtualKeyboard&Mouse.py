from time import sleep

import autopy
import cv2
import cvzone
import numpy as np
import pyautogui
from pynput.keyboard import Controller

import HandTrackingModule as htm

cap = cv2.VideoCapture(0)
wCam, hCam = 1280, 820
frameR = 90
smoothening = 7
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.8)

wScr, hScr = autopy.screen.size()

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", " ", ".", "/"]]

keyboard = Controller()


def drawAll(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)
    for button in buttonList:
        x, y = button.pos
        cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)
        cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]),
                      (255, 0, 0), cv2.FILLED)
        cv2.putText(imgNew, button.text, (x + 40, y + 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

    out = img.copy()
    alpha = 0.4
    mask = imgNew.astype(bool)
    # print(mask.shape)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
    return out


class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

while True:
    success, img = cap.read()
    # img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)
    img = drawAll(img, buttonList)

    if lmList:
        x10, y10 = lmList[4][1], lmList[4][2]
        x20, y20 = lmList[8][1], lmList[8][2]
        cx, cy = (x10 + x20) // 2, (y10 + y20) // 2
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()
        cv2.rectangle(img, (10, 400), (1270, 720), (0, 0, 255), 2)

        if fingers[1] == 1 and fingers[2] == 0:
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        # if fingers[4]==1 and fingers[1]==0:

        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)

            if length < 100:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
            if length < 50:
                pyautogui.click(sleep(0.3))
        if fingers[1] == 0 and fingers[2] == 1:
            pyautogui.click(button='right')
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            if x < lmList[4][1] < x + w and y < lmList[4][2] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 4, img, draw=False)

                if l < 60:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    sleep(0.5)

    # cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
