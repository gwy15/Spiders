# 说明

这个仓库是我平时写的一些爬虫或者自动下载器之类的。
全部项目基于 python 3.6.0+ 写成并运行，不保证其他版本能正常运行。

## bilibili_ass_danmu_getter

根据 av 号或者正版番组的番组号，下载 b 站的弹幕并转化为 ass 格式，方便直接用播放器播放。

+ xml 转 ass 部分的代码使用了 [danmu2ass](https://danmu2ass.codeplex.com/) 的代码。
+ 目前支持单P 一般视频、多P 一般视频，单集正版番组，多集正版番组下载。
+ 更改了原 xml 转 ass 的弹幕位置算法和显示效果，看起来更舒服。

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

## ZhihuDaily

目前只实现了爬取标题，以后会添加一点内容。

## weiboAlbum

针对一个用户的相册进行爬取。目前只能爬取 24 张图片，待完善。

需要说明的是，为了避免登陆验证，用户需要在 weiboAlbum 的目录下建立一个`config.json`，保存用户的 headers，一般只需要 Cookie 和 User-Agent 就可以了。

例如
>>>
    {
        "headers" : {
            "Cookie":"I'm Cookie",
            "User-Agent":"I'm User-Agent"
        }
    }

这样。

## Pixiv

爬取 Pixiv 搜索结果页的图片

* 单张插画
* 多张集合
* [x] 暂不支持动画

用法：
> py ./main.py エロマンガ先生 1000users入り page=5

代表搜索关键字为“エロマンガ先生 1000users入り”，保存前 5 页结果。

需要主意的是，需要在目录下建立`config.json`，形式如下

    {
        "headers":{
            "Cookie":"Copy your cookie here",
            "Host":"www.pixiv.net",
            "User-Agent":"your UA"
        }
    }

没有过多增加鲁棒性，所以有时候会有服务器断开连接的情况。重新跑一次（不会重复下载存在的文件）一般能解决问题。