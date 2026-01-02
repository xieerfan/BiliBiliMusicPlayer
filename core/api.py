from bilibili_api import channel_series, video

async def fetch_all_videos(season_id):
    series = channel_series.ChannelSeries(id_=season_id, type_=channel_series.ChannelSeriesType.SEASON)
    res = await series.get_videos()
    return res.get("archives", [])

async def get_single_video_info(bvid):
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    return info['title']