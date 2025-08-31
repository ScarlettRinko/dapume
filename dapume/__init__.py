"""
dapume - 线性乐谱渲染器

一个用于将线性乐谱转换为 MIDI 文件或音频的 Python 包。

线性乐谱是一种使用 ASCII 字符书写简单乐谱的方式，支持：
- 简谱记号 (1-7)
- 音高和时值修饰符
- 多轨演奏
- 和弦演奏
- 参数控制 (调号、BPM等)

主要类：
    LinearScore: 核心的线性乐谱解析和渲染类

示例用法：
    from dapume import LinearScore
    
    # 从文件读取乐谱
    with open('score.txt', 'r') as f:
        score_text = f.read()
    
    # 创建 LinearScore 实例
    score = LinearScore(score_text)
    
    # 保存为 MIDI 文件
    score.midi_file.save('output.mid')
"""

from .assets.linear_score import LinearScore
from .utils import midi_to_wav

__version__ = "0.3.1"
__author__ = "ScarlettRinko"
__email__ = "pleasantgoat2@yeah.net"

__all__ = ["LinearScore", "midi_to_wav"]
