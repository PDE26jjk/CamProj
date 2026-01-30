import sys


class ConsoleColors:
    """控制台颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'


class Console:
    """控制台输出类，支持不同颜色的输出方法"""

    def __init__(self, encoding='gbk'):
        """
        初始化Console类

        Args:
            encoding: 输出编码，默认为'gbk'
        """
        self.encoding = encoding
        self.colors = ConsoleColors

    def _write(self, message, color_code):
        """内部方法：将带颜色的消息写入stderr"""
        colored_message = f"{color_code}{message}{self.colors.ENDC}"
        sys.__stderr__.buffer.write(colored_message.encode(self.encoding))
        sys.__stderr__.flush()

    def _format_message(self, *args, **kwargs):
        """格式化消息参数"""
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        return sep.join(str(arg) for arg in args) + end

    def print(self, *args, **kwargs):
        """普通输出（白色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.WHITE)

    def info(self, *args, **kwargs):
        """信息输出（蓝色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.BLUE)

    def success(self, *args, **kwargs):
        """成功输出（绿色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.GREEN)

    def warning(self, *args, **kwargs):
        """警告输出（黄色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.WARNING)

    def error(self, *args, **kwargs):
        """错误输出（红色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.FAIL)

    def header(self, *args, **kwargs):
        """标题输出（紫色）"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.HEADER)

    def bold(self, *args, **kwargs):
        """粗体输出"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.BOLD)

    def underline(self, *args, **kwargs):
        """下划线输出"""
        message = self._format_message(*args, **kwargs)
        self._write(message, self.colors.UNDERLINE)

    def custom(self, *args, color=ConsoleColors.WHITE, **kwargs):
        """自定义颜色输出"""
        message = self._format_message(*args, **kwargs)
        self._write(message, color)


# 创建一个全局实例，方便直接使用
console = Console()


def console_print(*args, **kwargs):
    console.print(*args, **kwargs)
