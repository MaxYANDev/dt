import os
import requests
from github import Github
import schedule
import time
from git import Repo
import shutil 

def fetch_channel_data():
    url = 'https://mapi.dtradio.com.cn/api/v1/channel.php?'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return []

def parse_existing_m3u(repo_name, file_path_in_repo, local_file_path):
    repo_path = '/tmp/dt_repo'  # 临时存储仓库位置
    existing_channels = {}

    try:
        # 尝试从 GitHub 上获取文件
        if os.path.exists(repo_path):
            repo = Repo(repo_path)
        else:
            repo = Repo.clone_from(f'https://github.com/{repo_name}.git', repo_path)
        
        repo.remotes.origin.pull()

        repo_file_path = os.path.join(repo_path, file_path_in_repo)
        try:
            with open(repo_file_path, 'r', encoding='utf-8') as f:
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
            return existing_channels

        except FileNotFoundError:
            pass
        
    except Exception as e:
        print(f"Failed to fetch from GitHub: {str(e)}")

    # 如果从 GitHub 上获取失败，使用本地的文件
    try:
        with open(local_file_path, 'r', encoding='utf-8') as f:
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
        if name in existing_channels:
            old_info, old_url = existing_channels[name]
            base_old_url = old_url.split('?')[0]
            base_new_url = m3u_url.split('?')[0]
            if base_old_url == base_new_url:
                existing_channels[name] = (old_info, m3u_url)
            else:
                tvg_name = name
                group_title = "北京 山西"
                formatted_info = f'#EXTINF:-1 tvg-id="{tvg_name}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_title}",{tvg_name}\n'
                existing_channels[name] = (formatted_info, m3u_url)
        else:
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

def update_github(file_path, repo_name, file_path_in_repo, commit_message, github_token):
    repo_path = '/tmp/dt_repo'  # 临时存储仓库位置
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
    else:
        repo = Repo.clone_from(f'https://{github_token}@github.com/{repo_name}.git', repo_path)
    
    repo.remotes.origin.pull()

    repo_file_path = os.path.join(repo_path, file_path_in_repo)
    shutil.copyfile(file_path, repo_file_path)

    repo.git.add(file_path_in_repo)
    repo.index.commit(commit_message)
    repo.remotes.origin.push()

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

    #existing_channels = parse_existing_m3u('demo.m3u')
    repo_name = 'MaxYANDev/dt'  # Your repository details
    file_path_in_repo = 'channels.m3u'  # Path in your repository
    local_file_path = 'demo.m3u' 
    existing_channels = parse_existing_m3u(repo_name, file_path_in_repo, local_file_path)
    updated_channels = update_channels(existing_channels, new_channels)
    save_updated_m3u('channels.m3u', updated_channels)

    commit_message = 'Update channels.m3u'
    github_token = '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'  # Your GitHub token
    update_github('channels.m3u', repo_name, file_path_in_repo, commit_message, github_token)

def job():
    print("Running scheduled job...")
    generate_m3u()

if __name__ == "__main__":
    # Run the job immediately on startup
    job()
    # Schedule the job to run every hour
    schedule.every().hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
