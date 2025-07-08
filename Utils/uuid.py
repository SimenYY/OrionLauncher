import uuid
import hashlib

def offline(username: str) -> str:
    """
    生成离线模式下的 UUID
    
    根据用户名生成一个离线模式下的 UUID，使用 MD5 哈希算法
    
    参数:
        username (str): 玩家用户名
        
    返回:
        uuid.UUID: 生成的 UUID 对象
    """
    string_to_hash: str = "OfflinePlayer:" + username
    md5_hash: bytes = hashlib.md5(string_to_hash.encode('utf-8')).digest()
    return uuid.UUID(bytes=md5_hash, version=3)

if __name__ == "__main__":
    username: str = input("请输入用户名: ")
    print(offline(username))
