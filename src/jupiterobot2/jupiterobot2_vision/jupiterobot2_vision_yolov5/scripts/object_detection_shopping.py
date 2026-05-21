#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 Jupiter Robot Technology Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import rospy
# import cv2
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge, CvBridgeError
# import time
# from jupiterobot2_msgs.msg import YoloMsg, ObjectMsg
# from detector import Detector


# class ObjectDetection():

#     def __init__(self):
#         rospy.init_node('object_detection')

#         self.detector = Detector()

#         self.bridge = CvBridge()

#         rospy.Subscriber('usb_cam/image_raw', Image, self.image_callback, queue_size=1, buff_size=10000000)

#         # 定义数据的发布
#         self.info_pub = rospy.Publisher('yolo/object_info', YoloMsg, queue_size=1)
#         self.yolo_msgs_pub = YoloMsg()

#         self.pTime = 0


#     def image_callback(self, msg):
#         try:
#             img0 = self.bridge.imgmsg_to_cv2(msg, "bgr8")
#         except CvBridgeError as e:
#             rospy.logwarn(str(e))
#             return

#         img0, result = self.detector.detect(img0)
#         cTime = time.time()
#         fps = 1 / (cTime - self.pTime)
#         self.pTime = cTime

#         cv2.putText(img0, f"FPS:{fps:.1f}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

#         cv2.imshow('result', img0)
#         cv2.waitKey(1)

#         # 临时的数据类型存放在列表
#         object_list = []
#         for i, r in enumerate(result):
#             rospy.loginfo(
#                 f'{i}: ({r.u1}, {r.v1}) ({r.u2}, {r.v2})' +
#                 f' {r.name}, {r.conf:.3f}')
#             object_msgs_pub = ObjectMsg()
#             object_msgs_pub.id = i
#             object_msgs_pub.name = r.name
#             object_msgs_pub.conf = r.conf
#             object_msgs_pub.xmin = r.u1
#             object_msgs_pub.ymin = r.v1
#             object_msgs_pub.xmax = r.u2
#             object_msgs_pub.ymax = r.v2
#             object_list.append(object_msgs_pub)

#         # 将列表的数据类型赋值给自定义的数据类型
#         self.yolo_msgs_pub = object_list
#         self.info_pub.publish(self.yolo_msgs_pub)


# if __name__ == "__main__":
#     ObjectDetection()
#     try:
#         rospy.spin()
#     except KeyboardInterrupt:
#         pass
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import rospy
# import cv2
# import numpy as np
# import time
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge, CvBridgeError
# from detector import Detector

# # ==================== 购物车 UI 参数 ====================
# width, height = 500, 500
# row_height = 50
# col_widths = [200, 150, 100]  # Item, Quantity, Price
# columns = ["Item", "Quantity", "Price"]

# PRICE_MAP = {
# "apple": "RM 12.90",
#     "bread": "RM 8.90",
#     "coca": "RM 3.50",
#     "colgate": "RM 24.10",
#     "milk": "RM 9.90"
# }

# shopping_cart = []           # 全局购物车列表
# pending_item = None          # 当前等待用户确认的物品
# last_detect_time = 0         # 上次处理时间（防抖）

# # ==================== 购物车操作函数 ====================
# def add_to_cart(item_name):
#     price = PRICE_MAP.get(item_name, "RM 0.00")
#     for row in shopping_cart:
#         if row[0] == item_name:
#             row[1] += 1
#             return
#     shopping_cart.append([item_name, 1, price])
#     print(f"已添加：{item_name} x1")

# def remove_from_cart(item_name):
#     for row in shopping_cart:
#         if row[0] == item_name:
#             if row[1] > 1:
#                 row[1] -= 1
#                 print(f"已移除一个：{item_name} (剩余 {row[1]})")
#             else:
#                 shopping_cart.remove(row)
#                 print(f"已移除：{item_name} (已清空该物品)")
#             return
#     print(f"{item_name} 不在购物车中")

# def checkout():
#     if not shopping_cart:
#         print("购物车为空，无法结账")
#         return
#     total = calculate_total(shopping_cart)
#     print("\n" + "="*40)
#     print("              结    账")
#     print("-"*40)
#     for item, qty, price in shopping_cart:
#         print(f"{item:<20} x {qty:<3}  {price}")
#     print("-"*40)
#     print(f"总  计：{total:>8.2f} RM")
#     print("感谢您的购物！欢迎下次光临～")
#     print("="*40 + "\n")
#     shopping_cart.clear()

# def calculate_total(data):
#     total = 0.0
#     for row in data:
#         try:
#             price_str = row[2].replace("RM ", "").replace("RM", "").strip()
#             total += float(price_str) * int(row[1])
#         except:
#             continue
#     return total

# # ==================== UI 绘制函数 ====================
# def draw_table(data):
#     ui_img = np.ones((height, width, 3), dtype=np.uint8) * 255
#     x = 0
#     for i, col in enumerate(columns):
#         cv2.rectangle(ui_img, (x, 0), (x + col_widths[i], row_height), (0,0,0), 2)
#         cv2.putText(ui_img, col, (x + 10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
#         x += col_widths[i]

#     for r, row in enumerate(data[:6]):  # 最多显示6行
#         y1 = (r + 1) * row_height
#         y2 = y1 + row_height
#         x = 0
#         for c, val in enumerate(row):
#             cv2.rectangle(ui_img, (x, y1), (x + col_widths[c], y2), (0,0,0), 2)
#             cv2.putText(ui_img, str(val), (x + 10, y1 + 35),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
#             x += col_widths[c]

#     # 总计行
#     ty = 7 * row_height
#     cv2.rectangle(ui_img, (0, ty), (width, ty + row_height), (0,0,0), 2)
#     total = calculate_total(data)
#     cv2.putText(ui_img, f"totall: {total:.2f} RM", (10, ty + 35),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

#     cv2.imshow("Shopping Cart", ui_img)

# # ==================== 主类 ====================
# class ObjectDetection:
#     def __init__(self):
#         rospy.init_node('object_detection_shopping')
#         self.detector = Detector()
#         self.bridge = CvBridge()
#         rospy.Subscriber('usb_cam/image_raw', Image, self.image_callback, queue_size=1)
#         self.pTime = 0
#         print("=== 按键购物车系统启动 ===")
#         print("检测到物品后，按以下键操作：")
#         print("  A / a    → 添加到购物车")
#         print("  R / r    → 从购物车移除一个")
#         print("  C / c    → 结账（清空购物车）")
#         print("  其他键   → 忽略本次物品")
#         print("============================\n")

#     def image_callback(self, msg):
#         global pending_item, last_detect_time

#         try:
#             img0 = self.bridge.imgmsg_to_cv2(msg, "bgr8")
#         except CvBridgeError as e:
#             rospy.logwarn(str(e))
#             return

#         img0, result = self.detector.detect(img0)

#         # 计算 FPS
#         cTime = time.time()
#         fps = 1 / (cTime - self.pTime) if cTime > self.pTime else 0
#         self.pTime = cTime
#         cv2.putText(img0, f"FPS:{fps:.1f}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 3)

#         cv2.imshow('Detection Result', img0)

#         # 处理检测到的物品
#         current_time = time.time()
#         for r in result:
#             if r.conf < 0.2:
#                 continue
#             item_name = r.name

#             # 防重复：新物品 + 间隔 > 4秒
#             if pending_item is None and (current_time - last_detect_time > 4.0):
#                 pending_item = item_name
#                 last_detect_time = current_time
#                 print(f"\n[检测到新物品] → {item_name}")
#                 print("请按键： [A]添加  [R]移除  [C]结账  [其他]忽略")
#                 break  # 一次只询问一个物品

#         # 统一处理键盘输入（非阻塞）
#         key = cv2.waitKey(1) & 0xFF
#         if pending_item is not None and key != 255:  # 有待确认物品 且 按下了键
#             if key in (ord('a'), ord('A')):
#                 add_to_cart(pending_item)
#             elif key in (ord('r'), ord('R')):
#                 remove_from_cart(pending_item)
#             elif key in (ord('c'), ord('C')):
#                 checkout()
#             else:
#                 print(f"忽略物品：{pending_item}")

#             pending_item = None  # 清空等待状态

#         draw_table(shopping_cart)
#         # cv2.waitKey(1) 已经在这里，不需要额外调用


# if __name__ == "__main__":
#     try:
#         ObjectDetection()
#         rospy.spin()
#     except KeyboardInterrupt:
#         print("\n程序已通过 Ctrl+C 退出")
#     finally:
#         cv2.destroyAllWindows()

import rospy
import json
from std_msgs.msg import String
import cv2
import numpy as np
import time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from detector import Detector
from std_msgs.msg import String


# ==================== 购物车 UI 参数 ====================
width, height = 500, 500
row_height = 50
col_widths = [200, 150, 100]  # Item, Quantity, Price
columns = ["Item", "Quantity", "Price"]

PRICE_MAP = {
"apple": "RM 1.90",
    "bread": "RM 8.90",
    "coca": "RM 3.50",
    "colgate": "RM 24.6",
    "milk": "RM 9.90"
}

shopping_cart = []           # 全局购物车列表
pending_item = None          # 当前等待用户确认的物品
last_detect_time = 0         # 上次处理时间（防抖）
def on_checkout_callback(self, msg):
    if msg.data == "CHECKOUT_NOW":
        rospy.loginfo("收到语音结账信号，正在执行结账...")
        self.checkout()  # 你原有的结账函数（print 清单、计算总价、清空购物车等）
        self.recommend_dishes()  # 你原有的推荐函数

# 如果没有，添加一个示例 checkout 函数
def checkout(self):
    if not shopping_cart:
        print("购物车为空，无法结账")
        return

    total = calculate_total(shopping_cart)
    print("\n=== 结账清单 ===")
    for item in shopping_cart:
        print(f"{item[0]} x {item[1]}   {item[2]}")
    print(f"总计: RM {total:.2f}")
    shopping_cart.clear()  # 清空购物车（根据需求加）
    draw_table(shopping_cart)  # 更新 UI

# 确保每次购物车变化时发布更新（你已有类似）
    self.publish_cart()
# ==================== 购物车操作函数 ====================
def add_to_cart(item_name):
    price = PRICE_MAP.get(item_name, "RM 0.00")
    for row in shopping_cart:
        if row[0] == item_name:
            row[1] += 1
            return
    shopping_cart.append([item_name, 1, price])
    
    print(f"已添加：{item_name} x1")

def remove_from_cart(item_name):
    for row in shopping_cart:
        if row[0] == item_name:
            if row[1] > 1:
                row[1] -= 1
                print(f"已移除一个：{item_name} (剩余 {row[1]})")
            else:
                shopping_cart.remove(row)
                print(f"已移除：{item_name} (已清空该物品)")
            return
    
    print(f"{item_name} 不在购物车中")
    

def checkout():
    if not shopping_cart:
        print("购物车为空，无法结账")
        return
    total = calculate_total(shopping_cart)
    print("\n" + "="*40)
    print("              结    账")
    print("-"*40)
    for item, qty, price in shopping_cart:
        print(f"{item:<20} x {qty:<3}  {price}")
    print("-"*40)
    print(f"总  计：{total:>8.2f} RM")
    print("感谢您的购物！欢迎下次光临～")
    print("="*40 + "\n")
    shopping_cart.clear()

def calculate_total(data):
    total = 0.0
    for row in data:
        try:
            price_str = row[2].replace("RM ", "").replace("RM", "").strip()
            total += float(price_str) * int(row[1])
        except:
            continue
    return total

# ==================== UI 绘制函数 ====================
def draw_table(data):
    ui_img = np.ones((height, width, 3), dtype=np.uint8) * 255
    x = 0
    for i, col in enumerate(columns):
        cv2.rectangle(ui_img, (x, 0), (x + col_widths[i], row_height), (0,0,0), 2)
        cv2.putText(ui_img, col, (x + 10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
        x += col_widths[i]

    for r, row in enumerate(data[:6]):  # 最多显示6行
        y1 = (r + 1) * row_height
        y2 = y1 + row_height
        x = 0
        for c, val in enumerate(row):
            cv2.rectangle(ui_img, (x, y1), (x + col_widths[c], y2), (0,0,0), 2)
            cv2.putText(ui_img, str(val), (x + 10, y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
            x += col_widths[c]

    # 总计行
    ty = 7 * row_height
    cv2.rectangle(ui_img, (0, ty), (width, ty + row_height), (0,0,0), 2)
    total = calculate_total(data)
    cv2.putText(ui_img, f"totall: {total:.2f} RM", (10, ty + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

    cv2.imshow("Shopping Cart", ui_img)

# ==================== 主类 ====================
class ObjectDetection:
    def __init__(self):
        rospy.init_node('object_detection_shopping')
        self.cart_pub = rospy.Publisher('/shopping/cart_update', String, queue_size=1, latch=True)
        self.detector = Detector()
        self.bridge = CvBridge()
        rospy.Subscriber('usb_cam/image_raw', Image, self.image_callback, queue_size=1)
        self.pTime = 0
        # 订阅语音识别结果（你已有 voiceWords 话题）
        rospy.Subscriber("voiceWords", String, self.voice_callback)
     
        
        # 用于防止重复触发
        self.last_checkout_time = 0
        self.checkout_cooldown = 5.0  # 5秒冷却，避免连发
        self.publish_cart()
        print("=== 按键购物车系统启动 ===")
        print("after the item is detected ，press the following keys to operate：")
        print("  A / a    → adding to shopping cart")
        print("  R / r    → remove one from the shopping cart")
        print("  C / c    → check out ")
        print("  else   → ignore this item")
        print("============================\n")
    
    def voice_callback(self, msg):
        text = msg.data.lower().strip()
        
        if "check out" in text or "checkout" in text:
            current_time = time.time()
            if current_time - self.last_checkout_time > self.checkout_cooldown:
                self.last_checkout_time = current_time
                print("\n" + "="*50)
                print("【语音触发】检测到 'check out'，正在结账...")
                self.checkout()
                self.recommend_dishes()
                print("="*50 + "\n")
    def publish_cart(self):
        cart_data = []
        for item in shopping_cart:  # 假设 shopping_cart 是全局列表 [name, qty, price]
            name, qty, price = item
            cart_data.append({"name": name, "quantity": qty, "price": price})
        
        msg = String()
        msg.data = json.dumps({
            "items": cart_data,
            "total": calculate_total(shopping_cart)  # 假设你有这个函数计算总价
        })
        self.cart_pub.publish(msg)
        
    def checkout(self):
        # 原有结账逻辑（你代码里应该已有类似函数）
        if not shopping_cart:
            print("shopping cart is empty！")
            return

        print("\n" + "-"*40)
        print("结账清单：")
        total = 0.0
        for item in shopping_cart:
            name = item[0]
            qty = item[1]
            price_str = item[2].replace("RM ", "").replace("$", "")
            try:
                price = float(price_str)
                subtotal = qty * price
                total += subtotal
                print(f"{name:15} × {qty:2}   {item[2]:>8}   小计 RM {subtotal:5.2f}")
            except:
                print(f"{name:15} × {qty:2}   {item[2]}   （价格解析失败）")
        
        print("-"*40)
        print(f"totall：RM {total:.2f}")
        print("thank you for your purchase！enjoy your meal~")
        
        # 清空购物车（根据你的需求决定是否清空）
        # shopping_cart.clear()
        # draw_table(shopping_cart)

    def recommend_dishes(self):
        """根据购物车物品，给出终端菜肴推荐"""
        if not shopping_cart:
            print("购物车为空，无推荐菜肴。")
            return

        print("\n根据您购买的食材，推荐以下家常菜：")
        print("-"*50)

        items_set = {item[0].lower() for item in shopping_cart if item[0]}

        # 简单硬编码规则（可根据 PRICE_MAP 里的物品扩展）
        recommendations = []

        if "apple" in items_set:
            recommendations.append("苹果沙拉（清爽开胃）")
            recommendations.append("苹果炖排骨（甜香可口）")

        if "milk" in items_set:
            recommendations.append("奶油蘑菇汤（温暖滋润）")
            recommendations.append("牛奶燕麦粥（早餐首选）")

        if "bread" in items_set:
            recommendations.append("法式吐司（加牛奶更好）")
            recommendations.append("蒜香面包（简单快手）")

        if "coca" in items_set or "cola" in items_set:
            recommendations.append("可乐鸡翅（经典下饭菜）")
            recommendations.append("冰镇可乐配炸鸡（周末享受）")

        if "colgate" in items_set:
            recommendations.append("（买了牙膏？建议饭后刷牙保护牙齿哦~）")

        if not recommendations:
            print("当前购物车物品暂无对应推荐菜谱，您可以尝试购买更多常见食材～")
        else:
            for i, dish in enumerate(recommendations, 1):
                print(f"{i}. {dish}")

        print("-"*50)
    
    def image_callback(self, msg):
        global pending_item, last_detect_time

        try:
            img0 = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError as e:
            rospy.logwarn(str(e))
            return

        img0, result = self.detector.detect(img0)

        # 计算 FPS
        cTime = time.time()
        fps = 1 / (cTime - self.pTime) if cTime > self.pTime else 0
        self.pTime = cTime
        cv2.putText(img0, f"FPS:{fps:.1f}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 3)

        cv2.imshow('Detection Result', img0)

        # 处理检测到的物品
        current_time = time.time()
        for r in result:
            if r.conf < 0.2:
                continue
            item_name = r.name

            # 防重复：新物品 + 间隔 > 4秒
            if pending_item is None and (current_time - last_detect_time > 4.0):
                pending_item = item_name
                last_detect_time = current_time
                print(f"\n[检测到新物品] → {item_name}")
                print("请按键： [A]add  [R]remove  [C]check out  [else]ignore")
                break  # 一次只询问一个物品

        # 统一处理键盘输入（非阻塞）
        key = cv2.waitKey(1) & 0xFF
        if pending_item is not None and key != 255:  # 有待确认物品 且 按下了键
            if key in (ord('a'), ord('A')):
                add_to_cart(pending_item)
            elif key in (ord('r'), ord('R')):
                remove_from_cart(pending_item)
            elif key in (ord('c'), ord('C')):
                checkout()
            else:
                print(f"忽略物品：{pending_item}")

            pending_item = None  # 清空等待状态
        self.publish_cart()
        draw_table(shopping_cart)
        # cv2.waitKey(1) 已经在这里，不需要额外调用


if __name__ == "__main__":
    try:
        ObjectDetection()
        rospy.spin()
    except KeyboardInterrupt:
        print("\n程序已通过 Ctrl+C 退出")
    finally:
        cv2.destroyAllWindows()
