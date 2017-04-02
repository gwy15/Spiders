# 说明

对普通的视频（不算番组的）：
+ 通过 av 号得到视频的（如果有分 P）所有分 P 的标题和 cid
    > http://www.bilibili.com/widget/getPageList?aid={av}
+ 通过上一步得到的 cid 下载 xml 格式弹幕，转化，以分 P 名保存。

对番组：
+ 通过番组编号 bangumi ID 得到分集的分集编号 episode ID 和标题和 av 号
    > http://bangumi.bilibili.com/jsonp/seasoninfo/{bangumiID}.ver?&jsonp=jsonp
+ 判断上一步中得到的 av 的个数：
    如果等于 1：共 av 号，类似普通分P视频处理
    如果等于分集数量：不同 av 号，依次处理