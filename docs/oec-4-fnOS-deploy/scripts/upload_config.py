"""
SCP 上传脚本 - 将配置文件上传到远程主机并强制覆盖
使用 paramiko 库实现无人值守 SCP 上传
"""
import csv
import sys
import os
import paramiko

def read_credentials(csv_path):
    """从 password.csv 读取主机凭据"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('IP地址', '').strip():
                return {
                    'host': row['IP地址'].strip(),
                    'username': row['用户名'].strip(),
                    'password': row['密码'].strip(),
                    'port': int(row['SSH端口'].strip()),
                    'note': row.get('备注', '').strip()
                }
    return None

def upload_files(csv_path, local_dir, remote_dir, files):
    """上传文件列表到远程主机"""
    creds = read_credentials(csv_path)
    if not creds:
        print(f"错误: 无法从 {csv_path} 读取凭据")
        sys.exit(1)

    print(f"连接到 {creds['host']}:{creds['port']}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(creds['host'], port=creds['port'],
                username=creds['username'], password=creds['password'])
    sftp = ssh.open_sftp()
    print("连接成功!")

    for local_file, remote_file in files:
        local_path = os.path.join(local_dir, local_file)
        remote_path = f"{remote_dir}/{remote_file}"
        
        if not os.path.exists(local_path):
            print(f"  [跳过] 本地文件不存在: {local_path}")
            continue
            
        print(f"  [上传] {local_file} -> {remote_path}")
        sftp.put(local_path, remote_path)
        print(f"  [完成] {local_file}")

    sftp.close()
    ssh.close()
    print("上传完成，连接已关闭。")

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH = os.path.join(BASE_DIR, 'password.csv')
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    REMOTE_DIR = '/vol1/docker/mycontainers/homelab-monitor'

    FILES = [
        ('docker-compose.yml', 'docker-compose.yml'),
        ('.env', '.env'),
    ]

    upload_files(CSV_PATH, CONFIG_DIR, REMOTE_DIR, FILES)
