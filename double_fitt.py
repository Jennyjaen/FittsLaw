import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
#from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import time
import random
import math
import datetime
import pandas as pd
import os
import pygame
'''
class Logger(QThread):
    def __init__(self):
        super().__init__()
        self.running=False

    def run(self):
        self.running=True
        while(self.running):
            time=datetime.datetime.now()
            date=time.strftime('%Y-%m-%d %H:%M:%S.%f')
            print("current mouse position: ", pg.position())
            self.sleep(1)
    def end(self):
        self.running=False
'''


#https://stackoverflow.com/questions/66847237/getting-mouse-position-doesnt-work-if-button-is-clicked
class MouseHelper(QObject):
    pressed = pyqtSignal(str, int, int, int, int)
    released = pyqtSignal(str, int, int, int, int)
    #pressed = pyqtSignal(QPoint)
    #released = pyqtSignal(QPoint)

    def __init__(self, window):
        super().__init__(window)
        self._window = window

        self.window.installEventFilter(self)

    @property
    def window(self):
        return self._window

    def eventFilter(self, obj, event):
        if self.window is obj:
            if event.type() == QEvent.MouseButtonPress:
                time=datetime.datetime.now()
                date=time.strftime('%Y-%m-%d %H:%M:%S.%f')
                self.pressed.emit(date, event.globalX(), event.globalY(),  event.x(), event.y())

            elif event.type() == QEvent.MouseButtonRelease:
                time=datetime.datetime.now()
                date=time.strftime('%Y-%m-%d %H:%M:%S.%f')
                self.released.emit(date,event.globalX(), event.globalY(), event.x(), event.y())
        return super().eventFilter(obj, event)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.logger=Logger()
        self.count=0 #현재가 몇회째 인지
        self.firstclick=0
        self.rad_dis= [[100, 500],[50, 500], [30, 500], [30, 100], [50, 100], [100, 1000], [50, 200], [50, 400]]#전체 실험 하고 싶은 조건 #radius, distance
        self.condition= 1  #몇가지 조건을
        #assert(len(self.rad_dis)== self.condition)
        self.start_radius=50
        self.task = 10 # 몇 번 반복할 것인지
        self.overshoot=0 #몇회 overshoot 했는지
        self.hovering=False
        self.release_start = False #버튼 밖으로 나가면 별도의 release가 없어도 시스템이 release로 처리함. 
        self.setWindowFlag(Qt.FramelessWindowHint) #상단바 없애는 기능
        self.new_condition()
        self.UiCompoents()
        self.start_time = 0
        self.start_click=False
        
    def new_condition(self):
        self.firstclick = 0
        rand_num=random.randrange(0, len(self.rad_dis))
        [self.radius, self.distance]=self.rad_dis.pop(rand_num)
        print(self.radius)

    
    def UiCompoents(self):
        self.start=QPushButton("Start", self)
        self.new_start_end()
        self.start.setGeometry(self.s_width, self.s_height, self.start_radius, self.start_radius)
        self.start.setStyleSheet("border-radius: "+str(self.start_radius//2)+"; background-color: darkgreen; ")
        self.start.pressed.connect(self.click_start)
        self.start.released.connect(self.start_release)
        self.end=QPushButton("End", self)
        self.end.setGeometry(self.e_width, self.e_height, self.radius, self.radius)
        self.end.setStyleSheet("border-radius:"+str(self.radius//2)+"; background-color: red; ")
        self.end.released.connect(self.click_end)
        self.showMaximized()

    def finish(self):
        self.finished=QPushButton("Finished", self)
        self.finished.setGeometry(500, 500, 500, 500)
        self.finished.setStyleSheet("background-color: yellow;")
        self.finished.clicked.connect(QCoreApplication.instance().quit)
        self.finished.show()
    
    def start_release(self):
        print("released")
        if(self.firstclick >= 2):
            self.firstclick =  0
            cursor = QCursor()
            QTest.qWait(100) #time.sleep의 pyqt 버전
            cursor_pos = cursor.pos()
            button_pos = self.start.mapToGlobal(self.start.rect().center())
            distance = math.sqrt((cursor_pos.x() - button_pos.x())**2 + (cursor_pos.y() - button_pos.y())**2)
            print(distance)
            if(distance < self.start_radius):
                self.end.setStyleSheet("border-radius: "+str(self.radius//2)+"; background-color: cyan;  border: 5px solid red;")
                QTest.qWait(100) #time.sleep의 pyqt 버전
                pygame.mixer.init(16000, -16, 1, 2048)
                pygame.mixer.music.load("wrong.mp3")
                pygame.mixer.music.play()

                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(30)
                pygame.mixer.quit() 

                self.start_click=False
                #self.logger.end()
                self.count+=1
                self.setMouseTracking(False)
                self.start.setMouseTracking(False)
                self.end.setMouseTracking(False)
                self.add_correct(1)
                if(self.count>=self.condition * self.task): #전체 task 마무리시 
                    self.start.setDisabled(True)
                    self.end.setDisabled(True)
                    df=pd.DataFrame(list(zip(timeline, trial, distance, radius, hovering, overshoot, start_x, start_y, end_x, end_y, global_x, global_y, local_x, local_y, correct)),
                    columns=['timeline', 'trial' , 'distance', 'radius', 'hovering', 'overshoot', 'start_x', 'start_y', 'end_x', 'end_y', 'global_x', 'global_y', 'local_x', 'local_y', 'correct'])
                    df.to_csv(str(timeline[0][-4:])+'.csv', index=False)
                    print("csv making done.")
                    self.finish()
                else:
                    if(self.count % self.task ==0):
                        self.new_condition()
                    self.new_start_end()
                    QTest.qWait(300) #time.sleep의 pyqt 버전
                    self.start.setGeometry(self.s_width, self.s_height, self.start_radius, self.start_radius)
                    self.end.setGeometry(self.e_width, self.e_height, self.radius, self.radius)
                    self.start.setStyleSheet("border-radius: "+str(self.start_radius//2)+"; background-color: green; ")
                    self.end.setStyleSheet("border-radius:"+str(self.radius//2)+"; background-color: red; ")
                    self.overshoot=0

    def click_start(self):
        #self.logger.start()
        if(self.firstclick ==0):
            self.firstclick =1
            self.start_time = datetime.datetime.now()
        elif(self.firstclick==1):
            print((datetime.datetime.now() - self.start_time).total_seconds() * 1000)
            if (datetime.datetime.now() - self.start_time).total_seconds() * 1000 <=500:
                self.setMouseTracking(True)
                self.start.setMouseTracking(True)
                self.end.setMouseTracking(True)
                self.start_click=True
                self.firstclick = 2
                self.start.setStyleSheet("border-radius: "+str(self.start_radius//2)+"; background-color: yellow; border: 5px solid darkgreen; ")
            else:
                self.start_time = datetime.datetime.now()

        else:
            self.firstclick = 0
            print("click is wrong")
        

    def click_end(self):
        print("end here")
        self.firstclick = 0
        print(str(self.count)+"  correct")
        '''
        filepath=os.path.join(os.getcwd(), 'correct.mp3')
        url=QUrl.fromLocalFile(filepath)
        content=QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()'''
  
        if(self.start_click):
            self.end.setStyleSheet("border-radius: "+str(self.radius//2)+"; background-color: yellow;  border: 5px solid red;")
            self.start_click=False
            QTest.qWait(100) #time.sleep의 pyqt 버전
            #time.sleep(0.1)
            pygame.mixer.init(16000, -16, 1, 2048)
            pygame.mixer.music.load("correct.mp3")
            pygame.mixer.music.play()

            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                clock.tick(30)
            pygame.mixer.quit()  
            #self.logger.end()
            self.count+=1
            self.setMouseTracking(False)
            self.start.setMouseTracking(False)
            self.end.setMouseTracking(False)
            self.add_correct(0)
            if(self.count>=self.condition * self.task): #전체 task 마무리시 
                self.start.setDisabled(True)
                self.end.setDisabled(True)
                df=pd.DataFrame(list(zip(timeline, trial, distance, radius, overshoot, hovering, start_x, start_y, end_x, end_y, global_x, global_y, local_x, local_y, correct)),
                columns=['timeline', 'trial' , 'distance', 'radius', 'overshoot', 'hovering', 'start_x', 'start_y', 'end_x', 'end_y', 'global_x', 'global_y', 'local_x', 'local_y', 'correct'])
                df.to_csv(str(timeline[0][-4:])+'.csv', index=False)
                print("csv making done.")
                self.finish()
            else:
                if(self.count % self.task ==0):
                    self.new_condition()
                self.new_start_end()
                QTest.qWait(200) #time.sleep의 pyqt 버전
                self.start.setGeometry(self.s_width, self.s_height, self.start_radius, self.start_radius)
                self.end.setGeometry(self.e_width, self.e_height, self.radius, self.radius)
                self.start.setStyleSheet("border-radius: "+str(self.start_radius//2)+"; background-color: green; ")
                self.end.setStyleSheet("border-radius:"+str(self.radius//2)+"; background-color: red; ")
                self.overshoot=0
                #self.end.setStyleSheet("border-radius: "+str(self.radius//2)+"; background-color: yellow;  border: 5px solid red;")
        else:
            print("Invalid Click")
            self.start_click=False


    def new_start_end(self):
        self.s_width=random.randrange(0, width- self.start_radius)
        self.s_height=random.randrange(0, height- self.start_radius)
        rand_rad=random.randrange(0, 360)
        self.e_width=self.s_width + self.distance * math.cos(math.radians(rand_rad))+ self.start_radius - self.radius
        self.e_height=self.s_height + self.distance * math.sin(math.radians(rand_rad))+ self.start_radius - self.radius
        while(self.e_width <0 or self.e_width>width - self.radius or self.e_height<0 or self.e_height>height - self.radius):
            rand_rad=random.randrange(0, 360)
            self.e_width=self.s_width + self.distance * math.cos(math.radians(rand_rad))
            self.e_height=self.s_height + self.distance * math.sin(math.radians(rand_rad))
        self.e_height=int(self.e_height)
        self.e_width=int(self.e_width)

    def mouseReleaseEvent(self, event):
        #end 버튼 위에서 떼도 다 이쪽으로 들어오는 듯함...
        if(self.start_click): #button 위 클릭은 감지 못하는 듯.
            cursor = QCursor()
            cursor_pos = cursor.pos()
            button_pos = self.end.mapToGlobal(self.end.rect().center())
            distance = math.sqrt((cursor_pos.x() - button_pos.x())**2 + (cursor_pos.y() - button_pos.y())**2)

            if(distance > self.radius):
                print(str(self.count)+"  wrong")
                self.end.setStyleSheet("border-radius: "+str(self.radius//2)+"; background-color: cyan;  border: 5px solid red;")
                QTest.qWait(100) #time.sleep의 pyqt 버전
                pygame.mixer.init(16000, -16, 1, 2048)
                pygame.mixer.music.load("wrong.mp3")
                pygame.mixer.music.play()

                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(30)
                pygame.mixer.quit() 

                self.start_click=False
                #self.logger.end()
                self.count+=1
                self.setMouseTracking(False)
                self.start.setMouseTracking(False)
                self.end.setMouseTracking(False)
                self.add_correct(1)
            else:
                self.end.setStyleSheet("border-radius: "+str(self.radius//2)+"; background-color: yellow;  border: 5px solid red;")
                self.start_click=False
                QTest.qWait(100) #time.sleep의 pyqt 버전
                #time.sleep(0.1)
                pygame.mixer.init(16000, -16, 1, 2048)
                pygame.mixer.music.load("correct.mp3")
                pygame.mixer.music.play()

                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(30)
                pygame.mixer.quit()  
                #self.logger.end()
                self.count+=1
                self.setMouseTracking(False)
                self.start.setMouseTracking(False)
                self.end.setMouseTracking(False)
                self.add_correct(0)
            if(self.count>=self.condition * self.task): #전체 task 마무리시 
                self.start.setDisabled(True)
                self.end.setDisabled(True)
                df=pd.DataFrame(list(zip(timeline, trial, distance, radius, hovering, overshoot, start_x, start_y, end_x, end_y, global_x, global_y, local_x, local_y, correct)),
                columns=['timeline', 'trial' , 'distance', 'radius', 'hovering', 'overshoot', 'start_x', 'start_y', 'end_x', 'end_y', 'global_x', 'global_y', 'local_x', 'local_y', 'correct'])
                df.to_csv(str(timeline[0][-4:])+'.csv', index=False)
                print("csv making done.")
                self.finish()
            else:
                if(self.count % self.task ==0):
                    self.new_condition()
                self.new_start_end()
                QTest.qWait(300) #time.sleep의 pyqt 버전
                self.start.setGeometry(self.s_width, self.s_height, self.start_radius, self.start_radius)
                self.end.setGeometry(self.e_width, self.e_height, self.radius, self.radius)
                self.start.setStyleSheet("border-radius: "+str(self.start_radius//2)+"; background-color: green; ")
                self.end.setStyleSheet("border-radius:"+str(self.radius//2)+"; background-color: red; ")
                self.overshoot=0

    def add_correct(self, wrong): #Correct: 0 Wrong: 1
        assert(len(timeline)- len(correct)>0)
        for i in range(len(timeline)- len(correct)):
            correct.append(wrong)
        assert(len(timeline)- len(correct)==0)
            
    def mousePressEvent(self, event):
        print("press!!")

    def mouseMoveEvent(self, event):
        if(self.firstclick ==2):
            self.start_release ==True
        #print((self.e_width + self.radius//2 - event.x())**2 +(self.e_height + self.radius//2 - event.y())**2 , (self.radius//2)**2)
        if((self.e_width + self.radius//2 - event.x())**2 +(self.e_height + self.radius//2 - event.y())**2 <=(self.radius//2)**2):
            if(self.hovering==False):
                self.overshoot+=1
            self.hovering=True
        else:
            self.hovering=False
        time=datetime.datetime.now()
        date=time.strftime('%Y-%m-%d %H:%M:%S.%f')
        timeline.append(date)
        trial.append(self.count)
        radius.append(self.radius)
        distance.append(self.distance)
        global_x.append(event.globalX())
        global_y.append(event.globalY())
        local_x.append(event.x())
        local_y.append(event.y())
        start_x.append(self.s_width)
        start_y.append(self.s_height)
        end_x.append(self.e_width)
        end_y.append(self.e_height)
        overshoot.append(self.overshoot)
        if(self.hovering):
            hovering.append(1)
        else:
            hovering.append(0)
        #print(self.hovering)
        #print(event.globalX(), event.globalY(), event.x(), event.y())
        #global position 이 pyautogui로 받는 값과 동일. full screen 기준 x값은 동일, y값이 25px 작았음. : 위에 이름 창 때문이 아닐지 #상단바 없애니까 같아짐.

def add_press_info(time, g_x, g_y, x, y, pressed):
    timeline.append(time)
    trial.append(0)
    radius.append(0)
    distance.append(0)
    global_x.append(g_x)
    global_y.append(g_y)
    local_x.append(x)
    local_y.append(y)
    start_x.append(0)
    start_y.append(0)
    end_x.append(0)
    end_y.append(0)
    overshoot.append(0)
    hovering.append(pressed)
    return

app = QApplication(sys.argv)
screen=app.desktop().screenGeometry()
width, height= screen.width(), screen.height()
timeline=[]
global_x=[]
global_y=[]
local_x=[]
local_y=[]
trial=[]
radius=[]
distance=[]
overshoot=[]
hovering=[] # 0 : just moving 1: hovering around button #2: press #3 release
start_x=[]
start_y=[]
end_x=[]
end_y=[]
correct=[]

window = MyWindow()
window.show()
helper=MouseHelper(window.windowHandle())
helper.pressed.connect(lambda t, g_x, g_y, x,y: add_press_info(t, g_x, g_y, x, y, 2))
helper.released.connect(lambda t, g_x, g_y, x,y: add_press_info(t, g_x, g_y, x, y, 3))


app.exec_()