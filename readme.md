# 说明

这个仓库是我平时写的一些爬虫或者自动下载器之类的。

## bilibili_ass_danmu_getter

根据 av 号或者正版番组的番组号，下载 b 站的弹幕并转化为 ass 格式，方便直接用播放器播放。

+ xml 转 ass 部分的代码使用了 [danmu2ass](https://danmu2ass.codeplex.com/) 的代码。
+ 目前支持单P 一般视频、多P 一般视频，单集正版番组，多集正版番组下载。

## NetMusic

调用网易云音乐的一些 api，目前可以实现的是搜索和歌词。

+ 参考了 [这篇文章](http://moonlib.com/606.html)

## steam

调用 steam 的 api，查询软件/游戏的售价/打折情况。

+ 使用 MySQL 储存数据。
+ 使用多线程。
+ 可视化进度条

## zhuangbi.info

爬取 [zhuangbi.info](https://www.zhuangbi.info/) 的表情包

+ 储存图片使用其标题，结合 everything 斗图好帮手。
+ 使用多线程。
+ 可视化进度条
