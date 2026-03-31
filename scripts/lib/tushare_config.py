"""
Tushare配置管理器
用于管理和验证Tushare token配置
"""

import os
from pathlib import Path
import tushare as ts


class TushareConfig:
    """Tushare配置管理器"""
    
    def __init__(self, token_path: str = None):
        """
        初始化配置管理器
        
        Args:
            token_path: token文件路径
        """
        if token_path is None:
            # 默认路径
            self.token_path = Path.home() / '.openclaw' / 'workspace' / '.credentials' / 'tushare_token.txt'
        else:
            self.token_path = Path(token_path)
        
        self.token = self._load_token()
        self.pro_api = None
    
    def _load_token(self) -> str:
        """从文件加载token"""
        try:
            with open(self.token_path, 'r', encoding='utf-8') as f:
                token = f.read().strip()
                return token
        except FileNotFoundError:
            raise ValueError(f"Tushare token文件不存在: {self.token_path}")
        except Exception as e:
            raise ValueError(f"读取Tushare token失败: {e}")
    
    def set_token(self, token: str):
        """设置token并保存到文件"""
        # 验证token格式（简单的验证）
        if not isinstance(token, str) or len(token) != 48:
            raise ValueError("无效的Tushare token格式")
        
        # 确保目录存在
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存token
        with open(self.token_path, 'w', encoding='utf-8') as f:
            f.write(token.strip())
        
        # 更新内存中的token
        self.token = token.strip()
        print(f"Tushare token已保存到: {self.token_path}")
    
    def get_token(self) -> str:
        """获取token"""
        return self.token
    
    def validate_token(self) -> bool:
        """验证token是否有效"""
        try:
            # 设置token
            ts.set_token(self.token)
            
            # 尝试获取API实例
            pro = ts.pro_api()
            
            # 尝试获取一些基础数据来验证
            df = pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20230102')
            
            if df is not None and len(df) > 0:
                print("✅ Tushare token 验证成功")
                self.pro_api = pro
                return True
            else:
                print("❌ Tushare token 验证失败 - 无法获取数据")
                return False
                
        except Exception as e:
            print(f"❌ Tushare token 验证失败: {e}")
            return False
    
    def get_pro_api(self):
        """获取Tushare专业版API实例"""
        if self.pro_api is None:
            if not self.validate_token():
                raise ValueError("Tushare token无效，无法获取API实例")
        return self.pro_api


def initialize_tushare():
    """初始化Tushare配置"""
    try:
        config = TushareConfig()
        print(f"正在验证Tushare配置...")
        print(f"Token文件路径: {config.token_path}")
        
        if config.validate_token():
            print("🎉 Tushare配置初始化成功!")
            return config
        else:
            print("⚠️ Tushare配置存在问题，请检查token")
            return None
            
    except Exception as e:
        print(f"❌ Tushare配置初始化失败: {e}")
        return None


def get_tushare_instance():
    """获取Tushare实例的便捷函数"""
    config = TushareConfig()
    if config.validate_token():
        return config.get_pro_api()
    else:
        raise ValueError("Tushare token无效")


if __name__ == "__main__":
    # 测试配置
    print("=== Tushare配置测试 ===")
    
    config = initialize_tushare()
    
    if config:
        # 测试获取数据
        try:
            pro = config.get_pro_api()
            # 获取上证指数最近一天的数据
            df = pro.index_daily(ts_code='000001.SH', start_date='20230101', end_date='20230102')
            print(f"数据获取成功，获取到 {len(df)} 条记录")
            print(df.head())
        except Exception as e:
            print(f"数据获取测试失败: {e}")
    else:
        print("配置验证失败，无法进行测试")