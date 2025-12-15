import time

class RandomSeedGenerator:
    """
    基于时间的随机种子生成器
    """
    
    @staticmethod
    def generate_seed() -> int:
        """
        基于当前时间生成随机种子
        
        Returns:
            int: 基于当前时间的随机种子
        """
        # 使用当前时间的纳秒级时间戳
        return int(time.time_ns()) % (2 ** 31)