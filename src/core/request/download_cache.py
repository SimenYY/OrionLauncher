"""下载缓存管理模块。

提供智能缓存机制，避免重复下载已存在且校验正确的文件。
支持文件完整性验证、缓存索引管理等功能。
"""

import json
import os
import hashlib
import time
import logging
from typing import Dict, Optional, Set, List
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    file_path: str
    url: str
    size: int
    sha1: str
    download_time: float
    last_verified: float
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """从字典创建"""
        return cls(**data)


class DownloadCache:
    """下载缓存管理器
    
    管理已下载文件的缓存信息，避免重复下载。
    提供文件完整性验证、缓存清理等功能。
    """
    
    def __init__(self, cache_dir: str = ".download_cache"):
        """初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.cache_file = self.cache_dir / "download_cache.json"
        self.cache_data: Dict[str, CacheEntry] = {}
        
        # 缓存配置
        self.max_cache_age = 7 * 24 * 3600  # 7天
        self.verify_interval = 24 * 3600  # 24小时重新验证一次
        
        # 加载缓存数据
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存数据"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, entry_data in data.items():
                    try:
                        self.cache_data[key] = CacheEntry.from_dict(entry_data)
                    except Exception as e:
                        logger.warning(f"加载缓存条目失败: {key} - {e}")
                
                logger.info(f"加载缓存数据完成，共 {len(self.cache_data)} 个条目")
            else:
                logger.info("缓存文件不存在，创建新的缓存")
                
        except Exception as e:
            logger.error(f"加载缓存数据失败: {e}")
            self.cache_data = {}
    
    def _save_cache(self):
        """保存缓存数据"""
        try:
            # 清理过期缓存
            self._cleanup_expired_cache()
            
            # 保存到文件
            data = {key: entry.to_dict() for key, entry in self.cache_data.items()}
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"缓存数据已保存，共 {len(self.cache_data)} 个条目")
            
        except Exception as e:
            logger.error(f"保存缓存数据失败: {e}")
    
    def _cleanup_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache_data.items():
            # 检查缓存是否过期
            if current_time - entry.download_time > self.max_cache_age:
                expired_keys.append(key)
                continue
            
            # 检查文件是否仍然存在
            if not os.path.exists(entry.file_path):
                expired_keys.append(key)
        
        # 删除过期条目
        for key in expired_keys:
            del self.cache_data[key]
            logger.debug(f"删除过期缓存条目: {key}")
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存条目")
    
    def _generate_cache_key(self, url: str, file_path: str) -> str:
        """生成缓存键
        
        Args:
            url: 文件URL
            file_path: 文件路径
            
        Returns:
            缓存键
        """
        # 使用URL和文件路径的组合作为键
        key_data = f"{url}:{file_path}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def is_file_cached(self, url: str, file_path: str, expected_size: int = 0, 
                      expected_sha1: str = "") -> bool:
        """检查文件是否已缓存且有效
        
        Args:
            url: 文件URL
            file_path: 文件路径
            expected_size: 期望文件大小
            expected_sha1: 期望SHA1值
            
        Returns:
            文件是否已缓存且有效
        """
        cache_key = self._generate_cache_key(url, file_path)
        
        # 检查缓存中是否存在
        if cache_key not in self.cache_data:
            return False
        
        entry = self.cache_data[cache_key]
        current_time = time.time()
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.debug(f"缓存文件不存在: {file_path}")
            del self.cache_data[cache_key]
            return False
        
        # 检查文件大小
        if expected_size > 0:
            actual_size = os.path.getsize(file_path)
            if actual_size != expected_size:
                logger.debug(f"文件大小不匹配: {file_path} (期望: {expected_size}, 实际: {actual_size})")
                del self.cache_data[cache_key]
                return False
        
        # 检查是否需要重新验证SHA1
        if expected_sha1 and (current_time - entry.last_verified > self.verify_interval):
            if self._verify_file_sha1(file_path, expected_sha1):
                # 更新验证时间
                entry.last_verified = current_time
                self._save_cache()
                logger.debug(f"文件SHA1验证通过: {file_path}")
                return True
            else:
                logger.debug(f"文件SHA1验证失败: {file_path}")
                del self.cache_data[cache_key]
                return False
        
        # 如果有SHA1要求但缓存中的SHA1不匹配
        if expected_sha1 and entry.sha1 != expected_sha1:
            logger.debug(f"缓存SHA1不匹配: {file_path}")
            del self.cache_data[cache_key]
            return False
        
        logger.debug(f"文件已缓存且有效: {file_path}")
        return True
    
    def add_to_cache(self, url: str, file_path: str, size: int, sha1: str = ""):
        """添加文件到缓存
        
        Args:
            url: 文件URL
            file_path: 文件路径
            size: 文件大小
            sha1: 文件SHA1值
        """
        cache_key = self._generate_cache_key(url, file_path)
        current_time = time.time()
        
        entry = CacheEntry(
            file_path=file_path,
            url=url,
            size=size,
            sha1=sha1,
            download_time=current_time,
            last_verified=current_time
        )
        
        self.cache_data[cache_key] = entry
        self._save_cache()
        
        logger.debug(f"文件已添加到缓存: {file_path}")
    
    def _verify_file_sha1(self, file_path: str, expected_sha1: str) -> bool:
        """验证文件SHA1
        
        Args:
            file_path: 文件路径
            expected_sha1: 期望SHA1值
            
        Returns:
            验证是否通过
        """
        try:
            sha1_hash = hashlib.sha1()
            
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha1_hash.update(chunk)
            
            actual_sha1 = sha1_hash.hexdigest()
            return actual_sha1.lower() == expected_sha1.lower()
            
        except Exception as e:
            logger.error(f"验证文件SHA1时发生错误: {file_path} - {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        total_files = len(self.cache_data)
        total_size = sum(entry.size for entry in self.cache_data.values())
        
        # 统计各种文件类型
        file_types = {}
        for entry in self.cache_data.values():
            ext = os.path.splitext(entry.file_path)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "file_types": file_types,
            "cache_dir": str(self.cache_dir),
            "cache_file": str(self.cache_file)
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.cache_data.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("缓存已清空")


# 全局缓存实例
_global_cache: Optional[DownloadCache] = None


def get_download_cache() -> DownloadCache:
    """获取全局下载缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = DownloadCache()
    return _global_cache
