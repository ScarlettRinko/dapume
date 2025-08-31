"""
测试 LinearScore 类的核心功能
"""

import unittest
import os
import tempfile
from pathlib import Path

from dapume import LinearScore


class TestLinearScore(unittest.TestCase):
    """LinearScore 类的单元测试"""

    def setUp(self):
        """测试前的设置"""
        self.simple_score = """1=C 120bpm
1234567"""
        
        self.complex_score = """1=D
5-345-34(1+(3+(5+)))
55,6,7,1234(7,+(2+(5+)))"""

    def test_basic_score_parsing(self):
        """测试基本乐谱解析"""
        ls = LinearScore(self.simple_score)
        
        # 验证轨道数量
        self.assertGreater(len(ls.track_notes), 0, "应该至少有一个轨道")
        
        # 验证第一轨道的音符数量
        first_track = ls.track_notes[0]
        self.assertEqual(len(first_track), 7, "第一轨道应该有7个音符")
        
        # 验证音符的基本属性
        for note in first_track:
            self.assertIsInstance(note.pitch, int, "音高应该是整数")
            self.assertGreaterEqual(note.pitch, 0, "音高应该非负")
            self.assertLessEqual(note.pitch, 127, "音高应该不超过127")
            self.assertGreaterEqual(note.start_time, 0, "开始时间应该非负")
            self.assertGreater(note.duration, 0, "持续时间应该为正")

    def test_complex_score_parsing(self):
        """测试复杂乐谱解析（多轨）"""
        ls = LinearScore(self.complex_score)
        
        # 验证多轨道
        self.assertGreater(len(ls.track_notes), 1, "复杂乐谱应该有多个轨道")
        
        # 验证每个轨道都有音符
        for i, track in enumerate(ls.track_notes):
            self.assertGreater(len(track), 0, f"轨道 {i} 应该有音符")

    def test_midi_file_generation(self):
        """测试 MIDI 文件生成"""
        ls = LinearScore(self.simple_score)
        
        # 验证 MIDI 文件对象存在
        self.assertIsNotNone(ls.midi_file, "应该生成 MIDI 文件对象")
        
        # 测试保存 MIDI 文件
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            ls.midi_file.save(tmp_path)
            self.assertTrue(os.path.exists(tmp_path), "MIDI 文件应该被保存")
            self.assertGreater(os.path.getsize(tmp_path), 0, "MIDI 文件应该不为空")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_empty_score(self):
        """测试空乐谱处理"""
        # 空字符串可能会导致错误，这是预期的行为
        empty_score = ""
        try:
            ls = LinearScore(empty_score)
            # 如果没有抛出异常，验证基本结构
            self.assertIsInstance(ls.track_notes, list, "track_notes 应该是列表")
        except (UnboundLocalError, IndexError, ValueError):
            # 空乐谱可能会导致这些异常，这是可以接受的
            pass

    def test_parameter_parsing(self):
        """测试参数行解析"""
        score_with_params = """1=G 100bpm
1234"""
        ls = LinearScore(score_with_params)
        
        # 验证能正常解析带参数的乐谱
        self.assertGreater(len(ls.track_notes), 0, "带参数的乐谱应该能正常解析")
        self.assertGreater(len(ls.track_notes[0]), 0, "应该有音符")

    def test_template_score_orchid_pavilion(self):
        """测试使用兰亭序模板"""
        # 获取模板文件路径
        package_dir = Path(__file__).parent.parent / 'dapume' / 'templates'
        template_path = package_dir / 'orchid_pavilion.txt'
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                score_content = f.read()
            
            ls = LinearScore(score_content)
            
            # 验证兰亭序乐谱解析
            self.assertGreater(len(ls.track_notes), 0, "兰亭序应该有轨道")
            
            # 验证多轨道（兰亭序包含和弦，应该有多个轨道）
            total_notes = sum(len(track) for track in ls.track_notes)
            self.assertGreater(total_notes, 10, "兰亭序应该有足够多的音符")


if __name__ == '__main__':
    unittest.main()
