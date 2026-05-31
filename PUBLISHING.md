# PyLevelator 发布指南

## 准备工作

### 1. 安装依赖

```bash
pip install build twine cython numpy
```

### 2. 配置 PyPI Token

在 GitHub 仓库设置中添加 Secrets：
- `PYPI_API_TOKEN` - PyPI API token
- `TEST_PYPI_API_TOKEN` - TestPyPI API token

获取 Token：
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

## 本地构建测试

### 构建源码包和 wheel

```bash
# 清理旧文件
rm -rf build dist *.egg-info

# 构建
python setup_optimized.py sdist bdist_wheel

# 检查
twine check dist/*
```

### 测试安装

```bash
# 创建虚拟环境测试
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 安装
pip install dist/pylevelator-1.1.0-*.whl

# 测试
python -c "from pylevelator import Levelator; print('OK')"
```

## 发布到 TestPyPI

### 手动发布

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pylevelator
```

### 使用 GitHub Actions

1. 推送代码到 GitHub
2. 在 Actions 页面手动触发 workflow
3. 选择 "Publish to TestPyPI"

## 发布到 PyPI

### 方式 1: 创建 Release（推荐）

1. 在 GitHub 创建新 Release
2. Tag: `v1.1.0`
3. Title: `v1.1.0 - Optimized version`
4. Description: 复制 CHANGELOG
5. Publish release

GitHub Actions 会自动构建并发布到 PyPI。

### 方式 2: 手动发布

```bash
# 上传到 PyPI
twine upload dist/*
```

## 验证发布

```bash
# 安装
pip install pylevelator

# 测试
python -c "
from pylevelator.optimized_backend import OptimizedBackend
backend = OptimizedBackend()
print(backend.get_info())
"
```

## 版本号规范

遵循语义化版本：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修正

当前版本：`1.1.0`
- `1` - 主版本
- `1` - 新增优化版本
- `0` - 初始发布

## 发布检查清单

发布前确认：

- [ ] 所有测试通过
- [ ] 更新版本号（setup.py, pyproject.toml）
- [ ] 更新 CHANGELOG.md
- [ ] 更新 README.md
- [ ] 构建成功
- [ ] 本地测试安装成功
- [ ] TestPyPI 测试成功
- [ ] 创建 Git tag
- [ ] 推送到 GitHub

## 常见问题

### Q: 构建失败 - 找不到 numpy

**A**: 确保先安装 numpy：
```bash
pip install numpy
python setup_optimized.py bdist_wheel
```

### Q: OpenMP 链接错误

**A**: 
- Windows: 确保安装了 Visual Studio
- macOS: `brew install libomp`
- Linux: `sudo apt-get install libomp-dev`

### Q: wheel 不是平台特定的

**A**: 这是正常的，因为包含 Cython 扩展，会为每个平台构建特定的 wheel。

## 多平台构建

使用 cibuildwheel 构建多平台 wheel：

```bash
pip install cibuildwheel
cibuildwheel --platform linux
cibuildwheel --platform macos
cibuildwheel --platform windows
```

或使用 GitHub Actions 自动构建（已配置）。

## 回滚

如果发布有问题：

```bash
# 从 PyPI 删除版本（不推荐，只能删除一次）
# 联系 PyPI 支持

# 发布修复版本
# 增加 PATCH 版本号
```

## 联系方式

- GitHub Issues: https://github.com/KakaruHayate/pylevelator/issues
- Email: [your-email]
