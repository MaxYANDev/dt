import requests

url = 'https://mapi.dtradio.com.cn/api/v1/channel.php?'


response = requests.get(url)

if response.status_code == 200:

    data = response.json()

   
    channel_m3u_dict = {}

    for item in data:
        name = item.get('name')
        if name in ["新闻综合频道", "公共频道", "大同生活频道"]:
            channel_stream = item.get('channel_stream', [])
            if channel_stream:
                m3u8_url = channel_stream[0].get('m3u8')
                if m3u8_url:
                    channel_m3u_dict[name] = m3u8_url.replace("playlist.m3u8", "index.m3u8")

    # 生成指定格式的信息
    for name, m3u_url in channel_m3u_dict.items():
        tvg_name = name
        tvg_logo = "https://epg.112114.xyz/logo/cctv1.png"  # 你想要的logo地址
        group_title = "大同"  # 你想要的group title
        formatted_info = f'#EXTINF:-1 tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_title}", {tvg_name}\n{m3u_url}'
        print(formatted_info)

else:
    print("Failed to fetch data from API. Status code:", response.status_code)
