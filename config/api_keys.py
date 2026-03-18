"""
API密钥管理模块

提供分层密钥管理、验证和降级机制，确保系统安全性和可用性。
"""

import os
import re
from typing import Optional, Dict, List
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeySource(Enum):
    """密钥来源"""
    ENV_VAR = "environment_variable"
    DOTENV = "dotenv_file"
    INTERACTIVE = "interactive_input"
    MOCK = "mock_mode"
    NONE = "no_key"


class APIKeyManager:
    """API密钥管理器"""
    
    # 支持的密钥类型
    KEY_TYPES = {
        "AI_API_KEY": {
            "description": "AI服务API密钥",
            "pattern": r"^sk-[a-zA-Z0-9]{20,}$",
            "required": False,  # 支持降级模式
            "env_var": "AI_API_KEY"
        }
    }
    
    @staticmethod
    def get_key(key_type: str = "AI_API_KEY") -> Optional[str]:
        """
        获取API密钥（分层优先级）
        
        优先级：
        1. 环境变量
        2. .env文件
        3. 交互式输入（可选）
        4. 降级模式
        
        Args:
            key_type: 密钥类型
            
        Returns:
            API密钥或None
        """
        if key_type not in APIKeyManager.KEY_TYPES:
            logger.warning(f"未知的密钥类型: {key_type}")
            return None
        
        key_config = APIKeyManager.KEY_TYPES[key_type]
        env_var = key_config["env_var"]
        
        # 1. 环境变量（最高优先级）
        key = os.getenv(env_var)
        if key and APIKeyManager._validate_key(key, key_type):
            logger.info(f"✅ 从环境变量获取{key_type}")
            return key
        
        # 2. .env文件（开发环境）
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv(env_var)
            if key and APIKeyManager._validate_key(key, key_type):
                logger.info(f"✅ 从.env文件获取{key_type}")
                return key
        except ImportError:
            logger.warning("⚠️  python-dotenv未安装，跳过.env文件检查")
        except Exception as e:
            logger.warning(f"⚠️  加载.env文件失败: {e}")
        
        # 3. 交互式输入（可选）
        if os.getenv("INTERACTIVE_KEY_SETUP", "false").lower() == "true":
            key = APIKeyManager._get_key_interactive(key_type)
            if key and APIKeyManager._validate_key(key, key_type):
                logger.info(f"✅ 通过交互式输入获取{key_type}")
                return key
        
        # 4. 无密钥（降级模式）
        logger.warning(f"⚠️  未找到有效的{key_type}，将使用降级模式")
        return None
    
    @staticmethod
    def _validate_key(key: str, key_type: str) -> bool:
        """验证密钥格式"""
        if not key:
            return False
        
        if key_type not in APIKeyManager.KEY_TYPES:
            return False
        
        pattern = APIKeyManager.KEY_TYPES[key_type]["pattern"]
        return bool(re.match(pattern, key))
    
    @staticmethod
    def _get_key_interactive(key_type: str) -> Optional[str]:
        """交互式获取密钥"""
        try:
            print(f"\n🔑 请输入{key_type}: ", end="")
            import getpass
            key = getpass.getpass("")
            return key
        except:
            return None
    
    @staticmethod
    def get_key_with_source(key_type: str = "AI_API_KEY") -> Dict:
        """
        获取密钥及其来源信息
        
        Returns:
            {
                "key": "sk-...",
                "source": KeySource.ENV_VAR,
                "valid": True
            }
        """
        key_config = APIKeyManager.KEY_TYPES.get(key_type)
        if not key_config:
            return {
                "key": None,
                "source": KeySource.NONE,
                "valid": False,
                "error": f"未知的密钥类型: {key_type}"
            }
        
        env_var = key_config["env_var"]
        
        # 检查环境变量
        key = os.getenv(env_var)
        if key and APIKeyManager._validate_key(key, key_type):
            return {
                "key": key,
                "source": KeySource.ENV_VAR,
                "valid": True
            }
        
        # 检查.env文件
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv(env_var)
            if key and APIKeyManager._validate_key(key, key_type):
                return {
                    "key": key,
                    "source": KeySource.DOTENV,
                    "valid": True
                }
        except:
            pass
        
        # 检查是否启用模拟模式
        if os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true":
            return {
                "key": None,
                "source": KeySource.MOCK,
                "valid": True,
                "mock": True
            }
        
        return {
            "key": None,
            "source": KeySource.NONE,
            "valid": False
        }
    
    @staticmethod
    def validate_all_keys() -> Dict:
        """验证所有密钥"""
        results = {}
        
        for key_type, config in APIKeyManager.KEY_TYPES.items():
            key_info = APIKeyManager.get_key_with_source(key_type)
            results[key_type] = key_info
            
            if not key_info["valid"] and config["required"]:
                logger.error(f"❌ 缺少必需的密钥: {key_type}")
            elif not key_info["valid"]:
                logger.warning(f"⚠️  缺少可选的密钥: {key_type}")
            else:
                logger.info(f"✅ {key_type} 验证通过")
        
        return results
    
    @staticmethod
    def print_key_status():
        """打印密钥状态"""
        print("\n" + "=" * 60)
        print("🔑 API密钥状态检查")
        print("=" * 60)
        
        results = APIKeyManager.validate_all_keys()
        
        for key_type, info in results.items():
            source_name = info["source"].value.replace("_", " ").title()
            
            if info.get("mock"):
                print(f"  {key_type}: 🎭 模拟模式")
            elif info["valid"]:
                print(f"  {key_type}: ✅ 有效 ({source_name})")
                # 显示密钥前4位和后4位
                key = info["key"]
                if key and len(key) > 8:
                    masked = f"{key[:4]}...{key[-4:]}"
                    print(f"    密钥: {masked}")
            else:
                print(f"  {key_type}: ❌ 缺失")
        
        print("=" * 60)
        
        # 检查是否有必需密钥缺失
        missing_required = [
            key_type for key_type, info in results.items()
            if not info["valid"] and APIKeyManager.KEY_TYPES[key_type]["required"]
        ]
        
        if missing_required:
            print("\n🚨 错误: 缺少以下必需密钥:")
            for key_type in missing_required:
                config = APIKeyManager.KEY_TYPES[key_type]
                print(f"  - {key_type}: {config['description']}")
            print("\n💡 解决方案:")
            print("  1. 设置环境变量")
            print("  2. 创建 .env 文件")
            print("  3. 使用交互式配置")
            return False
        
        # 检查是否有可选密钥缺失
        missing_optional = [
            key_type for key_type, info in results.items()
            if not info["valid"] and not APIKeyManager.KEY_TYPES[key_type]["required"]
        ]
        
        if missing_optional:
            print("\n⚠️  警告: 缺少以下可选密钥:")
            for key_type in missing_optional:
                config = APIKeyManager.KEY_TYPES[key_type]
                print(f"  - {key_type}: {config['description']}")
            print("\n💡 提示: 系统将使用降级模式运行")
        
        return True


def main():
    """主函数（用于测试）"""
    print("🔧 API密钥管理器测试")
    print("=" * 60)
    
    # 测试密钥获取
    key = APIKeyManager.get_key("AI_API_KEY")
    if key:
        print(f"✅ 获取到AI_API_KEY: {key[:8]}...")
    else:
        print("⚠️  未获取到AI_API_KEY")
    
    # 打印状态
    APIKeyManager.print_key_status()


if __name__ == "__main__":
    main()