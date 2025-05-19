"""
L7benchmark 的默认配置实现

本文件既作为简单实现，也是创建自定义配置文件的参考指南。
默认配置遵循命令行参数指定的基本行为。

关键概念:
- 配置文件控制基准测试期间 HTTP 请求的生成
- 每个工作线程重复调用 generate_request 方法
- 配置文件可以维护状态并实现复杂序列
- 配置文件接收有关先前请求的信息以做出决策
"""

from mytypes import BaseProfile
from mytypes import Args, RequestInfo
from typing import Optional


class DefaultProfile(BaseProfile):
    """
    默认配置实现，简单地使用命令行参数中指定的方法重复请求相同的 URL。
    
    此配置展示了功能性配置所需的最小实现。
    您可以将其作为创建自己的自定义配置的起点。
    """

    def __init__(self, args: Args, first_url: str, hostname: str):
        """
        使用参数和初始状态初始化配置。
        
        参数:
            args: 解析为 Args 对象的命令行参数
            first_url: 要请求的初始 URL（如果使用了 --ip，则已应用 IP 解析）
            hostname: 用于 SNI 和 Host 标头的主机名（从原始 URL 提取）
            
        此方法是您应该初始化配置所需跟踪的任何状态的地方。
        """
        # 始终首先调用父类的 __init__ 以设置通用属性
        super().__init__(args=args, first_url=first_url, hostname=hostname)
        
        # 将第一个 URL 存储为我们的 last_url（我们将继续请求的 URL）
        self.last_url: str = first_url
        
        # 将状态码初始化为默认成功值
        self.last_status_code: int = 200
        
        # 您可以在此处为自定义配置添加更多初始化：
        # - 从文件加载测试数据
        # - 初始化计数器、状态机
        # - 准备身份验证令牌
        # - 生成序列模式
        # - 创建 URL、标头或有效负载池
        

    def generate_request(self, 
          worker_id: int,
          last_url: Optional[str],
          last_status_code: Optional[int],        
        ) -> RequestInfo:
        """
        生成由工作线程发出的下一个请求。
        
        此方法会在每次需要生成新请求时被调用。
        它是你的配置文件逻辑的核心。
        
        参数:
            worker_id: 调用工作线程的唯一 ID（从 0 到 connections 数量-1）
            last_url: 工作线程上一个请求的 URL（首次调用时为 None）
            last_status_code: 工作线程上一个请求的 HTTP 状态码（首次调用时为 None）
            
        返回:
            包含下一个 HTTP 请求所需所有详细信息的 RequestInfo 对象
            
        实现策略:
        - 使用 worker_id 进行负载分配（不同的工作线程可以测试不同的端点）
        - 使用 last_status_code 适应服务器响应
        - 在调用之间维护状态以实现序列
        - 生成动态数据负载
        """
        # 从命令行参数获取 HTTP 方法
        method = self.args.method
        
        # 在这个简单的实现中，我们始终使用相同的 URL
        this_url = self.last_url
        
        # 你可以在自定义配置文件中实现更复杂的逻辑：
        # - 实现请求序列（登录 -> 操作 -> 登出）
        # - 根据模式从 URL 池中选择
        # - 生成随机或顺序的查询参数
        # - 根据先前的响应状态进行调整
        # - 根据 worker_id 选择不同的端点
        # - 为 POST/PUT 方法创建请求主体
        # - 为特定请求实现自定义标头
        
        # 返回包含 HTTP 请求所有详细信息的 RequestInfo 对象
        return RequestInfo(
            method=method,            # HTTP 方法 (GET, POST 等)
            url=this_url,             # 请求的完整 URL
            hostname=self.hostname,   # 用于 SNI/Host 标头的主机名
            headers=self.custom_headers,  # 来自命令行的标头 + Host 标头
            body=None                 # 请求主体（用于 POST/PUT 方法）
        )
    
# 重要：始终将您的配置类导出为 'ExportedProfile'
# 这是基准测试工具发现您的配置的方式
ExportedProfile = DefaultProfile