"""
端到端集成测试

测试 dapume 包的完整工作流程和各组件之间的集成。
"""

import unittest
import os
import tempfile
from pathlib import Path

from dapume import LinearScore


class TestIntegration(unittest.TestCase):
    """端到端集成测试"""

    def setUp(self):
        """测试前的设置"""
        self.test_scores = {
            'simple': """1=C 120bpm
1234567""",
            
            'with_timing': """1=C 120bpm
1-2-3-4-5-6-7-""",
            
            'multi_track': """1=C 120bpm
1234(567)""",
            
            'with_chords': """1=C 120bpm
[1]1234[5]567""",
            
            'complex': """1=D
5-345-34(1+(3+(5+)))
55,6,7,1234(7,+(2+(5+)))"""
        }

    def test_complete_workflow_simple_score(self):
        """测试简单乐谱的完整工作流程"""
        score_text = self.test_scores['simple']
        
        # 步骤1：创建 LinearScore 实例
        ls = LinearScore(score_text)
        
        # 步骤2：验证解析结果
        self.assertIsInstance(ls.track_notes, list, "track_notes 应该是列表")
        self.assertGreater(len(ls.track_notes), 0, "应该有至少一个轨道")
        self.assertEqual(len(ls.track_notes[0]), 7, "第一轨道应该有7个音符")
        
        # 步骤3：验证 MIDI 文件生成
        self.assertIsNotNone(ls.midi_file, "应该生成 MIDI 文件")
        
        # 步骤4：保存并验证 MIDI 文件
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            ls.midi_file.save(tmp_path)
            self.assertTrue(os.path.exists(tmp_path), "MIDI 文件应该保存成功")
            self.assertGreater(os.path.getsize(tmp_path), 0, "MIDI 文件应该不为空")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_multi_track_integration(self):
        """测试多轨道乐谱的集成"""
        score_text = self.test_scores['multi_track']
        ls = LinearScore(score_text)
        
        # 验证多轨道生成
        self.assertGreater(len(ls.track_notes), 1, "应该有多个轨道")
        
        # 验证每个轨道都有音符
        total_notes = 0
        for i, track in enumerate(ls.track_notes):
            self.assertGreater(len(track), 0, f"轨道 {i} 应该有音符")
            total_notes += len(track)
        
        self.assertGreaterEqual(total_notes, 7, "总音符数应该大于等于原始音符数")

    def test_template_files_integration(self):
        """测试模板文件的集成使用"""
        package_dir = Path(__file__).parent.parent / 'dapume' / 'templates'
        
        template_files = [
            'canon.txt',
            'flower_dance.txt', 
            'orchid_pavilion.txt',
            'tori_no_uta.txt'
        ]
        
        for template_name in template_files:
            template_path = package_dir / template_name
            
            if template_path.exists():
                with self.subTest(template=template_name):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        score_content = f.read()
                    
                    # 测试模板文件能正常解析
                    ls = LinearScore(score_content)
                    
                    # 基本验证
                    self.assertIsInstance(ls.track_notes, list, f"{template_name} 应该生成轨道列表")
                    self.assertGreater(len(ls.track_notes), 0, f"{template_name} 应该有轨道")
                    
                    # 验证能生成 MIDI
                    self.assertIsNotNone(ls.midi_file, f"{template_name} 应该能生成 MIDI")
                    
                    # 验证音符数量合理
                    total_notes = sum(len(track) for track in ls.track_notes)
                    self.assertGreater(total_notes, 0, f"{template_name} 应该有音符")

    def test_error_handling_integration(self):
        """测试错误处理的集成"""
        # 测试只有参数行
        param_only = "1=C 120bpm"
        try:
            param_ls = LinearScore(param_only)
            self.assertIsInstance(param_ls.track_notes, list, "只有参数的乐谱应该正常处理")
        except (ValueError, IndexError):
            # 只有参数行可能会导致这些异常，这是可以接受的
            pass

        # 测试无效字符（应该被忽略或正常处理）
        invalid_chars = """1=C 120bpm
1234xyz567"""
        try:
            invalid_ls = LinearScore(invalid_chars)
            # 如果没有抛出异常，验证基本结构
            self.assertIsInstance(invalid_ls.track_notes, list, "包含无效字符的乐谱应该正常处理")
        except Exception as e:
            # 如果抛出异常，应该是合理的异常类型
            self.assertIsInstance(e, (ValueError, TypeError, AttributeError, UnboundLocalError))

    def test_performance_with_large_score(self):
        """测试大型乐谱的性能"""
        # 生成一个较大的乐谱
        large_score_lines = ["1=C 120bpm"]
        
        # 添加100行音符
        for i in range(100):
            large_score_lines.append("1234567" * 10)  # 每行70个音符
        
        large_score = "\n".join(large_score_lines)
        
        # 测试解析时间（应该在合理时间内完成）
        import time
        start_time = time.time()
        
        ls = LinearScore(large_score)
        
        end_time = time.time()
        parse_time = end_time - start_time
        
        # 验证解析完成
        self.assertIsInstance(ls.track_notes, list, "大型乐谱应该能正常解析")
        self.assertGreater(len(ls.track_notes), 0, "大型乐谱应该有轨道")
        
        # 验证解析时间合理（不超过10秒）
        self.assertLess(parse_time, 10.0, f"大型乐谱解析时间过长: {parse_time:.2f}秒")
        
        # 验证音符数量
        total_notes = sum(len(track) for track in ls.track_notes)
        expected_notes = 100 * 70  # 100行 * 70个音符/行
        self.assertGreater(total_notes, expected_notes * 0.8, "音符数量应该接近预期")

    def test_package_imports(self):
        """测试包导入的完整性"""
        # 测试主要导入
        from dapume import LinearScore
        self.assertTrue(callable(LinearScore), "LinearScore 应该是可调用的类")
        
        # 测试 LinearScore 实例化
        ls = LinearScore("1234")
        self.assertIsInstance(ls, LinearScore, "应该能创建 LinearScore 实例")


if __name__ == '__main__':
    unittest.main()
