import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs.dialogs import Messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import ads


class MapViewer():
    def __init__(self, mappath) -> None:
        # TK窗口基础设置

        self.root = ttk.Window(themename="cosmo")
        self.root.title("南京信息工程大学 校园地图导航系统")
        self.root.geometry("1800x900")
        self.root.wm_iconbitmap("ui/icon.ico")
        self.root.resizable(False, False)
        
        # TK窗口组件初始化
        self.imageViewer = ttk.Label(self.root, cursor="fleur")
        self.imageViewer.bind("<MouseWheel>",self.onMousewheel)  # 绑定滚轮事件
        self.imageViewer.bind("<ButtonPress-1>", self.startMove)  # 绑定鼠标左键事件
        #self.imageViewer.bind("<ButtonPress-3>", self.test)
        self.imageViewer.bind("<B1-Motion>", self.moveImage)  # 绑定鼠标左键移动事件

        self.image_pil = Image.open(mappath) # 加载图片，待优化

        # 地图相关初始化
        self.base_size = self.cauculateSize(self.image_pil) # 基础缩放倍率计算
        self.size = 1.0 # 缩放比例定义初始化
        self.height, self.width = None, None  # 地图图片大小定义
        self.imageViewer.configure(padding=(0, 0, 0, 0))  # 地图控件内边距初始化
        self.move_x, self.move_y = 0, 0  # 地图位置初始化
        self.displayImage(self.imageViewer, self.image_pil, self.size) # 图片展示
        self.imageViewer.place(x=400)

        # 右侧框架初始化
        self.frame = ttk.Frame(self.root, width=400, height=900)
        self.frame.place(x=0, y=0, relheight=1)

        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(expand=True, fill='both', anchor='center', pady=20)

        # Logo视图
        self.logo = ImageTk.PhotoImage(Image.open("ui/title.png"))
        self.logo_label = ttk.Label(self.main_frame, image=self.logo)
        self.logo_label.pack(pady=5, padx=25)  # Add padding to separate from the top and other widgets

        # 路径查询
        self.title_label = ttk.Label(self.main_frame, text="—————  路径查询  —————", font=("微软雅黑 Light", 11))
        self.title_label.pack(pady=5)

        self.navigate_input = ttk.Frame(self.main_frame)
        self.navigate_input.pack(side=ttk.TOP)

        self.input1 = ttk.Entry(self.navigate_input, width=12)
        self.input1.pack(side=ttk.LEFT,pady=5)

        self.arrow_label = ttk.Label(self.navigate_input, text=" → ", font=("微软雅黑 Light", 12))
        self.arrow_label.pack(side=ttk.LEFT,pady=5)

        self.input2 = ttk.Entry(self.navigate_input, width=12)
        self.input2.pack(side=ttk.LEFT,pady=5)

        self.button_input = ttk.Frame(self.main_frame)
        self.button_input.pack(side=ttk.TOP)
        self.button = ttk.Button(self.button_input, text="查询路径", command=self.navigateBotton, width=10, bootstyle="outline")
        self.button.pack(side=ttk.LEFT, pady=5, padx=15)
        self.button1 = ttk.Button(self.button_input, text="清除路径", command=self.refresh, width=10, bootstyle="outline")
        self.button1.pack(side=ttk.LEFT, pady=5, padx=15)
        


        self.title_label = ttk.Label(self.main_frame, text="—————  参观查询  —————", font=("微软雅黑 Light", 11))
        self.title_label.pack(pady=5)

        self.visit_frame = ttk.Frame(self.main_frame)
        self.visit_frame.pack(side=ttk.TOP)


        self.input3 = ttk.Entry(self.visit_frame, width=12)
        self.input3.pack(side=ttk.LEFT,pady=5)
        self.button3 = ttk.Button(self.visit_frame, text="参观路径", command=self.visitBotton, width=10, bootstyle="outline")
        self.button3.pack(side=ttk.LEFT, pady=5, padx=15)

        self.sf_label = ttk.Label(self.main_frame, text="等待查询...", font=("微软雅黑", 10), bootstyle="primary")
        self.sf_label.pack(side=ttk.TOP, pady=15)


        self.sf = ScrolledFrame(self.main_frame, autohide=True, bootstyle="round")
        self.sf.pack(fill=BOTH, expand=YES, padx=50, pady=10)
        
        self.sf_list = []

        self.sf_pic1 = ImageTk.PhotoImage(Image.open("ui/start.png"))
        self.sf_pic2 = ImageTk.PhotoImage(Image.open("ui/pass.png"))
        self.sf_pic3 = ImageTk.PhotoImage(Image.open("ui/end.png"))
        

        original_image = Image.open("ui/shadow.png")
        resized_image = original_image.resize((15, 900)) 

        # 将调整大小后的图像转换为Tkinter兼容的格式
        self.shadow = ImageTk.PhotoImage(resized_image)

        #  创建Label显示图像
        self.shadows = ttk.Label(self.root, image=self.shadow, padding=0)
        self.shadows.place(x=400, y=0)

        
        self.map = ads.Map()

        self.root.mainloop()
        

    def onMousewheel(self, event):
        """
        MapViewer滚轮事件。根据鼠标滚轮滑动，放大、缩小图片。
        """
        # 根据比例尺计算鼠标对应实际坐标
        real_x = (event.x - self.move_x) / self.size / self.base_size
        real_y = (event.y - self.move_y / 2) / self.size / self.base_size

        # 根据滚轮滚动方向调整缩放或其他操作
        delta = -1 if event.delta > 0 else 1  # 在Windows上，delta通常是120或-120
        if delta == -1:
            self.size += 0.25 if self.size < 3 else 0
        else:
            self.size -= 0.25 if self.size > 1 else 0
        
        # 更新移动位置
        self.move_x = event.x - (real_x * self.size * self.base_size)
        self.move_y = (event.y - (real_y * self.size * self.base_size))*2
        
        self.displayImage(self.imageViewer, self.image_pil, self.size)
        self.paddingRefresh()

    def displayImage(self, imageViewer, pil, size):
        """
        Mapviewer展示图片方法。接受一个PIL图片。
        """
        image_pil = pil.copy()  #创建副本

        #缩放后尺寸计算
        self.width = pil.size[0]*size*self.base_size
        self.height = pil.size[1]*size*self.base_size

        image_pil.thumbnail((self.width, self.height))  # PIL缩放
        image_tk = ImageTk.PhotoImage(image_pil)  # Tkinter对象转化

        imageViewer.configure(image = image_tk)  # 配置TK图像
        imageViewer.place_configure(width=self.width, height=self.height)  # 配置TK控件大小
        
        # 防止图像被垃圾回收
        imageViewer.image = image_tk
    
    def cauculateSize(self, image_pil):
        imagex, imagey = image_pil.size
        return max(1400 / imagex, 900 / imagey)

    def startMove(self, event):
        self.start_x, self.start_y = event.x, event.y
    
    def moveImage(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.start_x, self.start_y = event.x, event.y
        self.move_x += delta_x 
        self.move_y += delta_y *2

        self.paddingRefresh()

    def paddingRefresh(self):
        if self.move_x > 0:
            self.move_x = 0
        if self.move_y > 0:
            self.move_y = 0
        if self.move_x < 1400 - self.width: 
            self.move_x = -self.width + 1400
        if self.move_y / 2 < 900 - self.height:
            self.move_y =  (-self.height + 900) * 2

        self.imageViewer.configure(padding=(self.move_x, self.move_y, 0, 0))

    def draw(self, Path):
        point = [(node.x,node.y) for node in Path.path]
        draw = ImageDraw.Draw(self.image_pil)
        
        for i in range(len(point)-1):
            draw.line([point[i], point[i+1]], fill="#24adf3", width=8)

        for node in Path.path:
            if node != Path.start and node != Path.end:
                draw.ellipse((node.x-10, node.y-10, node.x+10, node.y+10), fill="#2780e3")
                draw.text((node.x, node.y), node.name if node.name!= None else '', fill="#2780e3", font=ImageFont.truetype("msyh.ttc", 40))
            else:
                draw.text((node.x, node.y), node.name, fill="#2780e3", font=ImageFont.truetype("msyh.ttc", 42))
                draw.ellipse((node.x-15, node.y-15, node.x+15, node.y+15), fill="#2780e3")


        self.image_pil = self.image_pil.copy()
        self.displayImage(self.imageViewer, self.image_pil, self.size)

    def navigateBotton(self):
        # 在这里处理按钮点击事件，例如获取输入框的值
        input1_value = self.input1.get()
        input2_value = self.input2.get()
        try:
            path = self.map.getPath(input1_value, input2_value)
            print(path)
            self.refresh()
            self.draw(path)
            self.showPathList(self.sf, self.sf_list, self.sf_label, path)
        except ads.LocationError:
            self.a = Messagebox.show_error("你的起点/终点输入有误", title='你的起点/终点输入有误', parent=self.root)
    
    def visitBotton(self):
        pass
    
    def showPathList(self, sf, sf_list, sf_label, path):
        for widget in sf.winfo_children():
            widget.destroy()
        
        sf_list.clear()
        sf_label.config(text=f"查询成功！\n当前路径{round(path.distance, 1)}米。")
        for _ in range(len(path.path)):
            sf_list.append(ttk.Frame(sf))
        
        for i in range(len(path.path)):
            sf_list[i].pack(side=ttk.TOP)
            ttk.Label(sf_list[i], image=self.sf_pic1 if i==0 else self.sf_pic2 if i!=len(path.path)-1 else self.sf_pic3).pack(side=ttk.LEFT)
            ttk.Label(sf_list[i], text=f"{path.path[i].name if path.path[i].name != None else '(路口)'}", font=("微软雅黑 Bold", 11), width=12).pack(side=ttk.LEFT, padx=5, pady=5)
            ttk.Label(sf_list[i], text=f"{path.path[i].neighbours[path.path[i+1]]}米" if i<len(path.path)-1 else '', font=("微软雅黑 Light", 9), width=8).pack(side=ttk.LEFT, padx=5, pady=5)


    def refresh(self):
        self.image_pil = Image.open("map.jpg") # 加载图片，待优化
        self.displayImage(self.imageViewer, self.image_pil, self.size) # 图片展示
       

if "__main__" == __name__:
    window = MapViewer("map.jpg")

