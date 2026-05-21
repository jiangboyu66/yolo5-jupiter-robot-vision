#!/usr/bin/python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
import json
import time

class VoiceShoppingCheckout:
    def __init__(self):
        rospy.init_node('voice_shopping_checkout', anonymous=True)
        self.checkout_pub = rospy.Publisher("/shopping/checkout", String, queue_size=1)
        # 订阅 PocketSphinx 识别结果
        rospy.Subscriber("/recognizer/output", String, self.voice_callback, queue_size=5)
        
        # 订阅购物车最新状态（来自 object_detection_shopping.py）
        self.latest_cart = {"items": [], "total": 0.0}
        rospy.Subscriber("/shopping/cart_update", String, self.cart_update_callback, queue_size=5)
        
        # 用于防止短时间内重复触发
        self.last_trigger_time = 0
        self.cooldown = 5.0  # 秒
        
        rospy.loginfo("voice check out node has been activated ，lisenting for key words：check out / checkout ")

    def cart_update_callback(self, msg):
        try:
            data = json.loads(msg.data)
            self.latest_cart = data
            # rospy.logdebug(f"购物车更新：{len(data['items'])} 件商品，总计 RM {data['total']:.2f}")
        except Exception as e:
            rospy.logwarn(f"购物车数据解析失败: {e}")

    def voice_callback(self, msg):
        text = msg.data.lower().strip()
        rospy.loginfo(f"voice recognization result: {text}")

        now = time.time()
        if now - self.last_trigger_time < self.cooldown:
            return

        trigger_keywords = [
            "check out", "checkout", "check-out",
            "结账", "买单", "结算", "结帐", "付款"
        ]

        if any(kw in text for kw in trigger_keywords):
            self.last_trigger_time = now
            rospy.loginfo("detected the check out order ！processing...")

            self.perform_checkout_and_recommend()

    def perform_checkout_and_recommend(self):
    # 先发布信号，让购物节点执行实际结账
        self.checkout_pub.publish(String(data="CHECKOUT_NOW"))
        rospy.loginfo("send the signal to shopping node already")

        # 然后本地打印（可选，保留作为备份）
        items = self.latest_cart.get("items", [])
        total = self.latest_cart.get("total", 0.0)

        if not items:
            print("\n" + "="*60)
            print("【语音结账】 shopping acrt is empty can not check out")
            print("="*60 + "\n")
            return

        print("\n" + "="*60)
        print("【voice trigger bill】 shopping list:")
        print("-"*60)
        for item in items:
            name = item["name"]
            qty = item["quantity"]
            price = item["price"]
            print(f"{name:<15} × {qty:2}    {price:>10}")
        print("-"*60)
        print(f"总  计：                  RM {total:.2f}")
        print("="*60)

        self.recommend_dishes_based_on_cart(items)


    def recommend_dishes_based_on_cart(self, items):
        print("\nBased on the items in your shopping cart, we recommend the following home-cooked dishes：")
        print("-"*60)

        item_names = {item["name"].lower() for item in items}

        recommendations = []

        # 核心推荐逻辑（可继续扩展）
        if "apple" in item_names or "苹果" in item_names:
            recommendations.append("Apple salad (healthier with yogurt)")
            recommendations.append("Apple Stewed Pork Ribs (Sweet and savory, a perfect dish to eat with rice)")

        if "milk" in item_names or "牛奶" in item_names:
            recommendations.append("Cream of mushroom soup (warm and nutritious)")
            recommendations.append("Milk cupcakes (simple afternoon tea)")

        if "bread" in item_names or "面包" in item_names:
            recommendations.append("French toast (drizzled with milk and honey)")
            recommendations.append("Garlic bread (ready in 5 minutes in the oven)")

        if "coca" in item_names or "cola" in item_names or "可乐" in item_names:
            recommendations.append("Cola Chicken Wings (Classic Sweet and Savory Flavor)")
            recommendations.append("Cola beef (a stew is very good with rice)")

        if "egg" in item_names or "鸡蛋" in item_names:
            recommendations.append("Stir-fried eggs with tomatoes (a quick and easy home-style dish)")
            recommendations.append("Fried rice with egg (a lifesaver for leftover rice)")

        if len(recommendations) == 0:
            print("  There are currently no matching recommended recipes for the items in your shopping cart.～")
            print("  It is recommended to buy more common ingredients (such as eggs, tomatoes, rice, etc.).")
        else:
            for i, dish in enumerate(recommendations, 1):
                print(f"  {i}. {dish}")

        print("-"*60 + "\n")


if __name__ == '__main__':
    try:
        VoiceShoppingCheckout()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass