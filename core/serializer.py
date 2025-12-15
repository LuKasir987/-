"""
序列化器基类 - 提供序列化和反序列化的通用接口
"""
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Generic, Type

T = TypeVar('T', bound='Serializer')


class Serializer(ABC, Generic[T]):
    """序列化器抽象基类，定义序列化和反序列化的接口"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        将对象转换为字典，用于序列化
        
        Returns:
            包含对象数据的字典
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """
        从字典创建对象，用于反序列化
        
        Args:
            data: 包含对象数据的字典
            
        Returns:
            创建的对象实例
        """
        pass
    
    def to_json(self) -> str:
        """
        将对象转换为JSON字符串
        
        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        从JSON字符串创建对象
        
        Args:
            json_str: JSON字符串
            
        Returns:
            创建的对象实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        将对象保存到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            保存成功返回True，失败返回False
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls: Type[T], file_path: str) -> T:
        """
        从文件加载对象
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的对象实例，失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            return cls.from_json(json_str)
        except Exception as e:
            print(f"加载文件失败: {e}")
            return None