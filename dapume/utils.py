"""
dapume 工具函数

提供辅助功能，如 MIDI 转 WAV 等。
"""

import subprocess


def midi_to_wav(filename, outname):
    """
    将 MIDI 文件转换为 WAV 音频文件
    
    Args:
        filename (str): 输入的 MIDI 文件路径
        outname (str): 输出的 WAV 文件路径
    
    Note:
        需要安装 FluidSynth 并配置 soundfont.sf2 文件
        
    Example:
        >>> from dapume import midi_to_wav
        >>> midi_to_wav('input.mid', 'output.wav')
    """
    line = 'fluidsynth -ni soundfont.sf2 %s -F %s -g 1' % (filename, outname)
    ex = subprocess.Popen(line, shell=True)
    ex.communicate()
    ex.wait()
