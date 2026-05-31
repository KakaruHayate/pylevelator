"""
测试 Cython 实现
"""

import sys
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def test_cython_build():
    """测试 Cython 是否成功编译"""
    print("="*70)
    print("测试 1: Cython 编译")
    print("="*70)

    try:
        import core_cython
        print("[OK] Cython 模块导入成功")
        print(f"  模块: {core_cython.__file__}")
        return True
    except ImportError as e:
        print(f"[FAIL] Cython 模块导入失败: {e}")
        print("  请先运行: python setup.py build_ext --inplace")
        return False


def test_cython_functions():
    """测试 Cython 函数"""
    print("\n" + "="*70)
    print("测试 2: Cython 函数")
    print("="*70)

    try:
        import numpy as np
        from core_cython import (
            calculate_rms_envelope_fast,
            calculate_gain_curve_fast,
            smooth_gains_fast,
            apply_gains_fast,
            apply_lookahead_limiter_fast
        )

        # 创建测试数据
        audio = np.random.randn(44100).astype(np.float32) * 0.1

        # 测试 RMS 计算
        rms = calculate_rms_envelope_fast(audio, 2048, 512)
        print(f"[OK] RMS 计算: {len(rms)} 个值")

        # 测试增益计算
        gains = calculate_gain_curve_fast(rms, 0.1, 20.0, -10.0)
        print(f"[OK] 增益计算: {len(gains)} 个值")

        # 测试平滑
        smoothed = smooth_gains_fast(gains, 100)
        print(f"[OK] 增益平滑: {len(smoothed)} 个值")

        # 测试应用增益
        processed = apply_gains_fast(audio[:len(gains)], gains)
        print(f"[OK] 应用增益: {len(processed)} 个样本")

        # 测试限幅器
        limited = apply_lookahead_limiter_fast(audio[:len(gains)], gains, 100, 0.98)
        print(f"[OK] 前瞻限幅: {len(limited)} 个值")

        return True

    except Exception as e:
        print(f"[FAIL] 函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cython_backend():
    """测试 Cython 后端"""
    print("\n" + "="*70)
    print("测试 3: Cython 后端")
    print("="*70)

    try:
        from cython_backend import CythonBackend

        backend = CythonBackend()

        if not backend.is_available():
            print("[FAIL] Cython 后端不可用")
            return False

        print("[OK] Cython 后端可用")
        info = backend.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"[FAIL] 后端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cython_performance():
    """测试 Cython 性能"""
    print("\n" + "="*70)
    print("测试 4: 性能测试")
    print("="*70)

    test_file = Path(__file__).parent.parent / "test_middle.wav"

    if not test_file.exists():
        print(f"[SKIP] 测试文件不存在: {test_file}")
        return True

    try:
        from cython_backend import CythonBackend

        backend = CythonBackend()
        output = Path(__file__).parent / "test_output_cython.wav"

        print(f"处理文件: {test_file.name}")

        def progress(filename, percent):
            if percent % 20 == 0:
                print(f"  进度: {percent}%")

        start = time.time()
        result = backend.process(test_file, output, progress_callback=progress)
        elapsed = time.time() - start

        print(f"[OK] 处理完成")
        print(f"  输出: {result}")
        print(f"  时间: {elapsed:.2f} 秒")
        print(f"  文件大小: {result.stat().st_size / 1024 / 1024:.2f} MB")

        return True

    except Exception as e:
        print(f"[FAIL] 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("="*70)
    print("Cython 实现测试套件")
    print("="*70)
    print()

    tests = [
        test_cython_build,
        test_cython_functions,
        test_cython_backend,
        test_cython_performance,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[FAIL] 测试异常: {e}")
            results.append(False)

    print("\n" + "="*70)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("="*70)

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
