class EventBus:
    """
    事件总线：解耦神器。
    让不同的系统（如：升级系统和引擎）通过发送消息通信，而不是直接调用。
    """
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, **kwargs):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(**kwargs)

# 创建全局唯一的实例
bus = EventBus()