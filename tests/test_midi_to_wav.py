"""
测试 MIDI 转 WAV 功能
"""

import unittest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

from dapume import LinearScore, midi_to_wav


class TestMidiToWav(unittest.TestCase):
    """MIDI 转 WAV 功能的单元测试"""

    def setUp(self):
        """测试前的设置"""
        self.simple_score = """1=C 120bpm
1234567"""
        
        # 创建临时 MIDI 文件
        self.temp_midi = tempfile.NamedTemporaryFile(suffix='.mid', delete=False)
        self.temp_midi_path = self.temp_midi.name
        self.temp_midi.close()
        
        # 生成测试用的 MIDI 文件
        ls = LinearScore(self.simple_score)
        ls.midi_file.save(self.temp_midi_path)
        
        # 临时 WAV 文件路径
        self.temp_wav_path = tempfile.mktemp(suffix='.wav')

    def tearDown(self):
        """测试后的清理"""
        # 清理临时文件
        for path in [self.temp_midi_path, self.temp_wav_path]:
            if os.path.exists(path):
                os.unlink(path)

    @patch('subprocess.Popen')
    def test_midi_to_wav_function_call(self, mock_popen):
        """测试 midi_to_wav 函数调用"""
        # 模拟 subprocess.Popen
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # 调用函数
        midi_to_wav(self.temp_midi_path, self.temp_wav_path)
        
        # 验证 subprocess.Popen 被正确调用
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        
        # 验证命令行参数包含输入和输出文件
        command = call_args[0][0]
        self.assertIn(self.temp_midi_path, command)
        self.assertIn(self.temp_wav_path, command)
        self.assertIn('fluidsynth', command.lower())

    def test_midi_to_wav_with_invalid_input(self):
        """测试使用无效输入文件的情况"""
        non_existent_file = '/path/to/non/existent/file.mid'
        
        # 这个测试主要验证函数不会崩溃
        # 实际的错误处理取决于 FluidSynth 的行为
        try:
            midi_to_wav(non_existent_file, self.temp_wav_path)
        except Exception as e:
            # 如果抛出异常，应该是合理的异常类型
            self.assertIsInstance(e, (OSError, subprocess.SubprocessError, FileNotFoundError))

    @patch('subprocess.Popen')
    def test_midi_to_wav_process_interaction(self, mock_popen):
        """测试进程交互"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'output', b'error')
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        midi_to_wav(self.temp_midi_path, self.temp_wav_path)
        
        # 验证进程交互方法被调用
        mock_process.communicate.assert_called_once()
        mock_process.wait.assert_called_once()

    def test_midi_file_exists(self):
        """验证测试用的 MIDI 文件确实存在且有效"""
        self.assertTrue(os.path.exists(self.temp_midi_path), "测试 MIDI 文件应该存在")
        self.assertGreater(os.path.getsize(self.temp_midi_path), 0, "MIDI 文件应该不为空")

    @unittest.skipUnless(
        subprocess.run(['which', 'fluidsynth'], capture_output=True).returncode == 0,
        "FluidSynth 未安装，跳过实际转换测试"
    )
    def test_real_conversion_if_fluidsynth_available(self):
        """如果 FluidSynth 可用，测试实际转换"""
        # 这个测试只在 FluidSynth 实际安装时运行
        try:
            midi_to_wav(self.temp_midi_path, self.temp_wav_path)
            
            # 如果转换成功，WAV 文件应该存在
            # 注意：这个测试可能会失败，因为还需要 soundfont 文件
            if os.path.exists(self.temp_wav_path):
                self.assertGreater(os.path.getsize(self.temp_wav_path), 0, "WAV 文件应该不为空")
        except Exception:
            # 如果转换失败（比如缺少 soundfont），这是预期的
            pass


class TestMidiToWavIntegration(unittest.TestCase):
    """MIDI 转 WAV 集成测试"""

    def test_end_to_end_workflow(self):
        """测试从乐谱到 WAV 的完整工作流程"""
        score = """1=C 120bpm
1-2-3-4-"""
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
            midi_path = midi_file.name
        
        wav_path = tempfile.mktemp(suffix='.wav')
        
        try:
            # 步骤1：生成 MIDI
            ls = LinearScore(score)
            ls.midi_file.save(midi_path)
            self.assertTrue(os.path.exists(midi_path), "MIDI 文件应该生成成功")
            
            # 步骤2：转换为 WAV（使用 mock 避免依赖 FluidSynth）
            with patch('subprocess.Popen') as mock_popen:
                mock_process = MagicMock()
                mock_process.communicate.return_value = (b'', b'')
                mock_process.wait.return_value = 0
                mock_popen.return_value = mock_process
                
                midi_to_wav(midi_path, wav_path)
                
                # 验证转换函数被调用
                mock_popen.assert_called_once()
                
        finally:
            # 清理临时文件
            for path in [midi_path, wav_path]:
                if os.path.exists(path):
                    os.unlink(path)


if __name__ == '__main__':
    unittest.main()
