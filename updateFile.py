import os

def update_channel_info(channel_info):
    # 分割字符串并提取group-title后的节目名称
    try:
        program_name = channel_info.split('group-title="')[1].split('",')[1].strip()
    except IndexError:
        # 处理没有group-title的情况
        program_name = channel_info.split(',')[-1].strip()
    
    # 检查tvg-id和tvg-name是否为空，如果是则添加
    if 'tvg-id="' in channel_info and 'tvg-id=""' in channel_info:
        channel_info = channel_info.replace('tvg-id=""', f'tvg-id="{program_name}"')
    elif 'tvg-id="' not in channel_info:
        channel_info = channel_info.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{program_name}"')
    
    if 'tvg-name="' in channel_info and 'tvg-name=""' in channel_info:
        channel_info = channel_info.replace('tvg-name=""', f'tvg-name="{program_name}"')
    elif 'tvg-name="' not in channel_info:
        channel_info = channel_info.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-name="{program_name}"')

    return channel_info

def process_m3u_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if line.startswith('#EXTINF:'):
            updated_line = update_channel_info(line)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    updated_content = ''.join(updated_lines)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"File '{file_path}' has been updated.")

if __name__ == "__main__":
    # 提示用户输入m3u文件路径
    file_path = input("请输入m3u文件的路径: ").strip()
    
    if os.path.isfile(file_path):
        process_m3u_file(file_path)
    else:
        print(f"文件路径 '{file_path}' 无效。")
