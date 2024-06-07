import requests
import os
import schedule
import time

def generate_m3u():
    url = 'https://mapi.dtradio.com.cn/api/v1/channel.php?'

    response = requests.get(url)

    if response.status_code == 200:
        
        data = response.json()

        channel_m3u_dict = {}

        for item in data:
            name = item.get('name')
            if name in ["新闻综合频道", "公共频道", "大同生活频道"]:
                channel_stream = item.get('channel_stream', [])
                
                logo_square_host = item.get("logo", {}).get("square", {}).get("host", "")
                logo_square_filename = item.get("logo", {}).get("square", {}).get("filename", "")
                tvg_logo = f"{logo_square_host}{logo_square_filename}"

                if channel_stream:
                    m3u8_url = channel_stream[0].get('m3u8')
                    if m3u8_url:
                        channel_m3u_dict[name] = (m3u8_url, tvg_logo)

        m3u_content = ""
        for name, (m3u_url, tvg_logo) in channel_m3u_dict.items():
            tvg_name = name
            group_title = "北京 山西"  
            formatted_info = f'#EXTINF:-1 tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_title}", {tvg_name}\n{m3u_url}\n'
            m3u_content += formatted_info
      
        with open('channels.m3u', 'w', encoding='utf-8') as f:
            f.write(m3u_content)

     
        os.system('git add channels.m3u')
        os.system('git commit -m "Update channels.m3u"')
        os.system('git push origin master')

generate_m3u()
#schedule.every().day.at("11:28").do(generate_m3u)
schedule.every(1).hours.do(generate_m3u)

while True:
    schedule.run_pending()
    time.sleep(60)  
