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

import rospy
from jupiterobot2_msgs.msg import YoloMsg, ObjectMsg  # 订阅检测结果
from std_msgs.msg import String  # 用于发布描述/建议
import time
from transformers import pipeline  # LLM
from gtts import gTTS  # TTS
import speech_recognition as sr  # STT
from detector import PRICE_MAP  # 复用价格映射（假设可导入）
import os  # 用于路径检查和文件清理
import subprocess  # 用于 mpg123 播放

class ObjectPostProcessing():
    def __init__(self):
        rospy.init_node('object_postprocessing')

        # 检查本地模型路径
        model_path = os.path.expanduser("~/catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiter_vision_yolov5/distilgpt2")
        if not os.path.exists(model_path):
            rospy.logerr("本地 distilgpt2 模型不存在！请检查 ~/catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiter_vision_yolov5/distilgpt2")

        # LLM 初始化（用 distilgpt2，本地加载，CPU 模式）
        try:
            self.llm = pipeline(
                'text-generation',
                model='distilgpt2',
                local_files_only=True,  # 强制使用本地模型
                device=-1,              # 强制 CPU
                trust_remote_code=False,
                torch_dtype='float32'   # 避免精度问题
            )
            rospy.loginfo("本地 distilgpt2 LLM 加载成功")
        except Exception as e:
            rospy.logerr(f"LLM 加载失败: {str(e)}")
            self.llm = None

        # 语音初始化
        self.recognizer = sr.Recognizer()  # STT

        # 订阅检测结果
        rospy.Subscriber('yolo/object_info', YoloMsg, self.detection_callback)

        # 发布自然语言描述/建议
        self.desc_pub = rospy.Publisher('shopping_description', String, queue_size=1)
        self.suggestion_pub = rospy.Publisher('shopping_suggestion', String, queue_size=1)

    def detection_callback(self, msg):
        detected_items = []
        unrecognized = []  # 用于异常处理

        for obj in msg:  # msg是ObjectMsg列表
            if obj.conf > 0.5:  # 阈值过滤
                price = PRICE_MAP.get(obj.name, "Unknown")
                item_str = f"{obj.name}, price {price}, conf {obj.conf:.2f}"
                detected_items.append(item_str)
            else:
                unrecognized.append(obj.name)  # 低置信度视为未识别

        # 生成自然语言描述
        if detected_items:
            desc = self.generate_description(detected_items)
            rospy.loginfo(f"Description: {desc}")
            self.desc_pub.publish(desc)
            self.speak(desc)  # TTS输出

            # 生成建议/食谱
            suggestion = self.generate_suggestion(detected_items)
            rospy.loginfo(f"Suggestion: {suggestion}")
            self.suggestion_pub.publish(suggestion)
            self.speak(suggestion)

        # 异常处理：未识别物品用LLM分类
        if unrecognized:
            for item in unrecognized:
                query = self.handle_unrecognized(item)
                rospy.loginfo(f"Reclassified {item} as: {query}")
                self.speak(f"Unknown item reclassified as {query}")

        # 可选：语音交互（STT听取用户查询）
        user_query = self.listen_for_query()
        if user_query:
            response = self.answer_query(user_query, detected_items)
            rospy.loginfo(f"User query response: {response}")
            self.speak(response)

    def generate_description(self, items):
        if self.llm is None:
            return "LLM 未加载，无法生成描述"
        prompt = f"Detected items: {', '.join(items)}. Generate a natural language description:"
        try:
            response = self.llm(
                prompt,
                max_length=50,
                num_return_sequences=1,
                pad_token_id=50256,  # 避免 padding 警告
                do_sample=True,
                temperature=0.7
            )[0]['generated_text']
            return response.strip()
        except Exception as e:
            rospy.logerr(f"生成描述失败: {e}")
            return "生成失败，请重试"

    def generate_suggestion(self, items):
        if self.llm is None:
            return "LLM 未加载，无法生成建议"
        prompt = f"Based on detected items {', '.join(items)}, suggest shopping tips, recipe, or advice:"
        try:
            response = self.llm(
                prompt,
                max_length=100,
                num_return_sequences=1,
                pad_token_id=50256,
                do_sample=True,
                temperature=0.7
            )[0]['generated_text']
            return response.strip()
        except Exception as e:
            rospy.logerr(f"生成建议失败: {e}")
            return "生成失败，请重试"

    def handle_unrecognized(self, item):
        if self.llm is None:
            return "LLM 未加载，无法分类"
        prompt = f"Classify this unrecognized item: {item}. Possible category:"
        try:
            response = self.llm(
                prompt,
                max_length=30,
                num_return_sequences=1,
                pad_token_id=50256,
                do_sample=True,
                temperature=0.7
            )[0]['generated_text']
            return response.strip()
        except Exception as e:
            rospy.logerr(f"分类失败: {e}")
            return "分类失败，请重试"

    def answer_query(self, query, items):
        if self.llm is None:
            return "LLM 未加载，无法回答查询"
        prompt = f"User query: {query}. Detected items: {', '.join(items)}. Answer:"
        try:
            response = self.llm(
                prompt,
                max_length=100,
                num_return_sequences=1,
                pad_token_id=50256,
                do_sample=True,
                temperature=0.7
            )[0]['generated_text']
            return response.strip()
        except Exception as e:
            rospy.logerr(f"回答查询失败: {e}")
            return "回答失败，请重试"

    def speak(self, text):
        try:
            lang = 'en'  # 或 'ms' for Malay
            tts = gTTS(text=text, lang=lang, slow=False)
            mp3_path = "/tmp/output.mp3"
            tts.save(mp3_path)
            # 使用 mpg123 播放（在 Ubuntu 上更稳定）
            subprocess.call(['mpg123', '-q', mp3_path])
            os.remove(mp3_path)  # 清理临时文件
        except Exception as e:
            rospy.logwarn(f"TTS 播放失败: {e}")
            print(f"[语音播报替代] {text}")  # 备选输出

    def listen_for_query(self):
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio)  # 需要网络
        except sr.UnknownValueError:
            rospy.logwarn("语音识别失败: 未检测到语音")
            return None
        except Exception as e:
            rospy.logwarn(f"STT 错误: {e} (如果无网络，可禁用此功能)")
            return None  # 如果无网络，返回 None 跳过

if __name__ == "__main__":
    ObjectPostProcessing()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass