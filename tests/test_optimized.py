"""
测试优化版本
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_optimized_backend():
    """测试优化版本"""
    print("="*70)
    print("优化版本性能测试")
    print("="*70)
    print()

    test_file = Path(__file__).parent.parent / "test_middle.wav"

    if not test_file.exists():
        print(f"[SKIP] 测试文件不存在: {test_file}")
        return False

    try:
        from optimized_backend import OptimizedBackend

        backend = OptimizedBackend()

        if not backend.is_available():
            print("[FAIL] 优化后端不可用")
            return False

        print("[OK] 优化后端可用")
        info = backend.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print()
        print(f"处理文件: {test_file.name}")

        def progress(filename, percent):
            if percent % 20 == 0:
                print(f"  进度: {percent}%")

        output = Path(__file__).parent / "test_output_optimized.wav"

        start = time.time()
        result = backend.process(test_file, output, progress_callback=progress)
        elapsed = time.time() - start

        print()
        print(f"[OK] 处理完成")
        print(f"  输出: {result}")
        print(f"  时间: {elapsed:.2f} 秒")
        print(f"  文件大小: {result.stat().st_size / 1024 / 1024:.2f} MB")

        # 对比
        print()
        print("="*70)
        print("性能对比")
        print("="*70)
        print(f"  原版 (C++):        3秒")
        print(f"  Cython (基础):    27秒")
        print(f"  Cython (优化):    {elapsed:.2f}秒")
        print()
        print(f"  加速比 (vs 基础): {27 / elapsed:.1f}x")
        print(f"  相对原版:         {elapsed / 3:.1f}x 慢")

        return True

    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_optimized_backend()
    sys.exit(0 if success else 1)
