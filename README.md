# 简易绘板 Place for Bot

[r/place](https://reddit.com/r/place) 和 [夏日绘板](https://live.bilibili.com/pages/1702/pixel-drawing)
的简单实现版本（含前后端）

## 简介

在线预览实时画板并能获取像素坐标，提供 API 给 QQ BOT、TG BOT 等机器人或小程序接入。

用户可以使用 BOT 在群聊中使用指令绘制像素，也可在群聊中获取当前画板整体预览。

## 已实现功能

- 前端
  - 从后端获取完整画板
  - 加载自定义图片作为画板（DEBUG用）
  - 加载自定义 TXT 作为画板（DEBUG用）
  - 鼠标悬浮在色板上的色块是悬浮显示 HEX 颜色
  - 鼠标滚轮缩放画板
  - 显示当前缩放倍速
  - 显示当前鼠标指针所指像素的坐标（用于在群聊中通过指令绘图）
- 后端
  - 在画板指定坐标处绘制单个像素
  - 获取完整画板
  - 获取部分画板
  - 获取完整画板 + 色板
  - 获取部分画板 + 色板
  - 接入的 BOT 需要登录后才能在画板上绘制（OAuth2，不提供注册功能）
  - 获取图片时的频率限制（同一 IP 每分钟只能获取 2 次）
  - 记录某人在某群使用某 BOT 在某刻进行了绘制（数据库）

## TODO

- [ ] 用户数据库（及基本权限）
- [ ] 添加新 BOT
- [ ] 取消登录用户获取图片时的频率限制（使用独立 API）
- [ ] 针对某人 / 某群的绘制频率限制
- [ ] 代码优化 & 清理
