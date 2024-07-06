import requests

def fetch_channel_data():
    url = 'https://mapi.dtradio.com.cn/api/v1/channel.php?'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return []

def parse_existing_m3u(file_path):
    existing_channels = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        channel_info = None
        for line in lines:
            if line.startswith("#EXTINF"):
                channel_info = line
            elif line.startswith("http") and channel_info:
                try:
                    channel_name = channel_info.split('group-title="')[1].split('"')[1].split(', ')[1]
                except IndexError:
                    try:
                        channel_name = channel_info.split('tvg-name="')[1].split('"')[0]
                    except IndexError:
                        continue
                existing_channels[channel_name] = (channel_info, line)
                channel_info = None
    except FileNotFoundError:
        pass

    return existing_channels

def update_channels(existing_channels, new_channels):
    for name, (m3u_url, tvg_logo) in new_channels.items():
        if name not in existing_channels:
            tvg_name = name
            group_title = "北京 山西"
            formatted_info = f'#EXTINF:-1 tvg-id="{tvg_name}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_title}",{tvg_name}\n'
            existing_channels[name] = (formatted_info, m3u_url)
    
    return existing_channels

def save_updated_m3u(file_path, channels):
    with open(file_path, 'w', encoding='utf-8') as f:
        for info, url in channels.values():
            f.write(info)
            f.write(url + '\n')

def generate_m3u():
    channel_data = fetch_channel_data()

    new_channels = {}
    for item in channel_data:
        name = item.get('name')
        if name in ["新闻综合频道", "公共频道", "大同生活频道"]:
            channel_stream = item.get('channel_stream', [])
            
            logo_square_host = item.get("logo", {}).get("square", {}).get("host", "")
            logo_square_filename = item.get("logo", {}).get("square", {}).get("filename", "")
            tvg_logo = f"{logo_square_host}{logo_square_filename}"

            if channel_stream:
                m3u8_url = channel_stream[0].get('m3u8')
                if m3u8_url:
                    new_channels[name] = (m3u8_url, tvg_logo)

    existing_channels = parse_existing_m3u('demo.m3u')
    updated_channels = update_channels(existing_channels, new_channels)
    save_updated_m3u('channels.m3u', updated_channels)

if __name__ == "__main__":
    generate_m3u()
