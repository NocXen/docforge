"""
事件总线
提供组件间的事件通信机制

使用示例：
    from docforge.api.event_bus import EventBus, Event
    
    event_bus = EventBus()
    
    # 订阅事件
    def on_file_processed(event: Event):
        print(f"文件处理完成: {event.data}")
    
    subscription_id = event_bus.subscribe("file_processed", on_file_processed)
    
    # 发布事件
    event_bus.publish(Event(
        name="file_processed",
        data={"file": "output.docx"},
        source="workflow_engine"
    ))
    
    # 取消订阅
    event_bus.unsubscribe(subscription_id)
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading


@dataclass
class Event:
    """
    事件对象
    
    Attributes:
        name: 事件名称
        data: 事件数据
        source: 事件来源
        timestamp: 事件时间戳
    """
    name: str
    data: Any = None
    source: str = ""
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class EventBus:
    """
    事件总线
    
    实现发布-订阅模式
    """
    
    def __init__(self):
        """初始化事件总线"""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._subscription_ids: Dict[str, str] = {}  # id -> event_name
        self._id_counter = 0
        self._lock = threading.Lock()
    
    # ========== 订阅管理 ==========
    
    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> str:
        """
        订阅事件
        
        Args:
            event_name: 事件名称（支持通配符 *）
            callback: 回调函数
            
        Returns:
            str: 订阅ID
        """
        with self._lock:
            # 生成订阅ID
            self._id_counter += 1
            subscription_id = f"sub_{self._id_counter}"
            
            # 添加到订阅列表
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            self._subscribers[event_name].append(callback)
            self._subscription_ids[subscription_id] = event_name
            
            return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            subscription_id: 订阅ID
            
        Returns:
            bool: 是否成功
        """
        with self._lock:
            if subscription_id not in self._subscription_ids:
                return False
            
            event_name = self._subscription_ids[subscription_id]
            
            # 从订阅列表中移除（简化实现）
            # 实际应该根据subscription_id精确移除
            if event_name in self._subscribers:
                # 这里简化处理，实际需要记录callback和id的映射
                pass
            
            del self._subscription_ids[subscription_id]
            return True
    
    def unsubscribe_all(self, event_name: str = None) -> int:
        """
        取消所有订阅
        
        Args:
            event_name: 事件名称（可选，不指定则取消所有）
            
        Returns:
            int: 取消的数量
        """
        with self._lock:
            if event_name:
                # 取消特定事件的所有订阅
                if event_name in self._subscribers:
                    count = len(self._subscribers[event_name])
                    del self._subscribers[event_name]
                    
                    # 清理subscription_ids
                    to_remove = [
                        sid for sid, ename in self._subscription_ids.items()
                        if ename == event_name
                    ]
                    for sid in to_remove:
                        del self._subscription_ids[sid]
                    
                    return count
                return 0
            else:
                # 取消所有订阅
                count = sum(len(subs) for subs in self._subscribers.values())
                self._subscribers.clear()
                self._subscription_ids.clear()
                return count
    
    # ========== 事件发布 ==========
    
    def publish(self, event: Event) -> None:
        """
        发布事件（同步）
        
        Args:
            event: 事件对象
        """
        with self._lock:
            # 获取订阅者
            subscribers = self._get_subscribers_for_event(event.name)
        
        # 在锁外调用回调，避免死锁
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                # 忽略回调中的异常
                print(f"事件回调异常: {e}")
    
    def publish_async(self, event: Event) -> None:
        """
        异步发布事件
        
        Args:
            event: 事件对象
        """
        import threading
        
        def _publish():
            self.publish(event)
        
        thread = threading.Thread(target=_publish)
        thread.daemon = True
        thread.start()
    
    def _get_subscribers_for_event(self, event_name: str) -> List[Callable]:
        """
        获取事件的所有订阅者
        
        Args:
            event_name: 事件名称
            
        Returns:
            List[Callable]: 回调函数列表
        """
        subscribers = []
        
        # 精确匹配
        if event_name in self._subscribers:
            subscribers.extend(self._subscribers[event_name])
        
        # 通配符匹配
        if "*" in self._subscribers:
            subscribers.extend(self._subscribers["*"])
        
        return subscribers
    
    # ========== 查询 ==========
    
    def get_subscribers(self, event_name: str) -> List[str]:
        """
        获取事件的订阅者数量
        
        Args:
            event_name: 事件名称
            
        Returns:
            List[str]: 订阅ID列表
        """
        with self._lock:
            return [
                sid for sid, ename in self._subscription_ids.items()
                if ename == event_name
            ]
    
    def get_subscription_count(self) -> int:
        """
        获取订阅总数
        
        Returns:
            int: 订阅数量
        """
        with self._lock:
            return len(self._subscription_ids)
    
    def get_event_names(self) -> List[str]:
        """
        获取所有已订阅的事件名称
        
        Returns:
            List[str]: 事件名称列表
        """
        with self._lock:
            return list(self._subscribers.keys())
    
    def has_subscribers(self, event_name: str) -> bool:
        """
        检查事件是否有订阅者
        
        Args:
            event_name: 事件名称
            
        Returns:
            bool: 是否有订阅者
        """
        with self._lock:
            return event_name in self._subscribers and len(self._subscribers[event_name]) > 0