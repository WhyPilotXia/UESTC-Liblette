import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import threading
import os
import re
from nonebot.params import RegexStr
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, \
    MessageSegment, Message, GroupMessageEvent, Event, escape
from nonebot import on_command, on_startswith, on_keyword, on_fullmatch, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.params import ArgPlainText, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.log import logger
import json
import io
import base64
from PIL import Image, ImageDraw, ImageFont


async def run(prompt: str):
    async with async_playwright() as playwright:
        # 启动浏览器
        browser = await playwright.chromium.launch(headless=False)  # 如果不需要GUI界面，请设置headless=True
        context = await browser.new_context()

        # 打开新页面
        page = await context.new_page()

        # 访问目标URL
        await page.goto('https://robot.chaoxing.com/coze/web?unitId=22855&robotId=34254f5f9c2a448d921cf0b41f6d4628')

        # 等待页面加载完成，并找到对应的textarea元素
        await page.wait_for_selector('#app > div > div.view > div.message-web-view > div.send-box > textarea',
                                     state='visible')

        # 在textarea中输入文本
        await page.fill('#app > div > div.view > div.message-web-view > div.send-box > textarea', prompt)

        # 模拟按下回车键提交
        await page.keyboard.press('Enter')

        # 定义选择器和超时时间
        timeout_ms = 40000  # 40秒，以毫秒为单位

        try:
            # 等待第一个选择器的元素出现
            content_selector = '#app > div > div.view > div.message-web-view > div.message-list-box > div.message-list > div > div.wrapper > div:nth-child(3) > div > div > div.message-body > div.message-body-content > div > div.machine-read-content-wrap > div > div > div.content.mark-down.done'
            content_element = await page.wait_for_selector(content_selector, timeout=timeout_ms)

            # 找到元素后等待3秒
            await page.wait_for_timeout(3000)

            # 获取其内容
            content_text = await content_element.text_content() if content_element else "未找到对应元素"
            print(f"Content: {content_text}")
            # 等待第二个选择器的元素出现
            reasoning_selector = '#app > div > div.view > div.message-web-view > div.message-list-box > div.message-list > div > div.wrapper > div:nth-child(3) > div > div > div.message-body > div.message-body-content > div > div.machine-read-content-wrap > div > div > div.reasoning.reasoning-expand > div.reasoning-content'
            reasoning_element = await page.wait_for_selector(reasoning_selector, timeout=timeout_ms)

            # 找到元素后等待3秒
            await page.wait_for_timeout(3000)

            # 获取其内容
            reasoning_text = await reasoning_element.text_content() if reasoning_element else "未找到对应元素"
            print(f"Reasoning: {reasoning_text}")
            return f'<{reasoning_text}>{content_text}'
        except PlaywrightTimeoutError:
            print("等待超时：未能在40秒内找到所有选择器的元素")
            return "等待超时：未能在40秒内找到所有选择器的元素"



        # 关闭浏览器前可以添加input()来保持窗口打开以便调试
        # input("按任意键关闭浏览器...")


# 使用async_playwright上下文管理器运行
async def main():
    async with async_playwright() as playwright:
        await run('你好')


# 运行异步主函数
if __name__ == '__main__':
    asyncio.run(main())

qw = on_message(rule=to_me(), priority=96, block=True)


@qw.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    text = str(event.get_message())
    result = await run(text)
    await qw.send(result)
