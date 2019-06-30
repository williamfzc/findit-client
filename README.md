# findit-client

[![image](https://img.shields.io/pypi/pyversions/requests.svg)](https://pypi.org/project/requests/)
[![Build Status](https://travis-ci.org/williamfzc/findit-client.svg?branch=master)](https://travis-ci.org/williamfzc/findit-client)
[![PyPI version](https://badge.fury.io/py/findit-client.svg)](https://badge.fury.io/py/findit-client)

Client for [findit](https://github.com/williamfzc/findit), with no opencv needed.

## 目的

- 旨在提供超低依赖的findit client，用于适应不同机器（尤其是无法安装opencv）的环境；
- 该client只依赖于http请求，只使用了requests，依赖环境与requests一致；
- 足够简单易用；

## 使用

### 服务器部署

参考文档：[这里](https://williamfzc.github.io/findit/#/usage/client+server?id=服务端部署)

在 0.1.4 及之后的版本，你将可以使用 `local_mode` 用于在本地启动一个临时服务器用于调试，尽管这并不是client的设计初衷：

```python
cli = FindItStandardClient(
    port=9410,
    local_mode=True,

    # 你的图片库根目录
    pic_root='tests/pics',

    # findit需要3.6+的python版本
    python_path='python3'
)
```

值得注意，这并不是一种推荐的正式使用方式，可能更适合你调试用。正式环境的server应该是独立的。

### 连接到服务器

本地服务器：

```python
from findit_client import FindItClient

cli = FindItClient(port=9410)
```

远程服务器：

```python
from findit_client import FindItClient

cli = FindItClient(host='123.45.67.8', port=9410)
```

### 获取完全的分析结果

我们希望在本地图片 `screen.png` 中寻找 `wechat_logo.png`（这里假设该图片已存在于服务器）

```python
from findit_client import FindItClient

cli = FindItClient()

result = cli.analyse_with_path('screen.png', 'wechat_logo.png')

# 默认使用引擎 template与feature
# 你可以直接使用 API 操作与获取 数据
# 或者在这些基础上自由定制你需要的API

# 获取特征匹配的原始数据
print(result.feature_engine.data)
# 获取模板匹配的目标点坐标
print(result.template_engine.get_target())
```

将会返回完整的结果，供开发者自由定制。这也是最核心的方法，其他的API几乎都是通过该方法而来。

它被设计得极为灵活，你可以在该API中传入findit本身支持的 **任何参数**，并以此对findit的行为进行干预！

例如，engine参数可以改变参与分析的引擎：

```python
result = cli.analyse_with_path('screen.png', 'wechat_logo.png', engine=['ocr', 'feature'])
```

例如 `engine_ocr_lang` 能够修改 OCR 引擎的分析语言：

```python
result = cli.analyse_with_path('screen.png', 'wechat_logo.png', engine=['ocr', 'feature'], engine_ocr_lang='chi_sim')
```

### 分析 opencv object

为了最小化client的依赖，默认的client并没有支持opencv。如果你希望直接识别opencv对象，你可以使用 `FindItStandardClient` 替代 `FindItClient`。

```python
from findit_client import FindItStandardClient
import cv2

cli = FindItStandardClient()

target_object = cv2.imread('tests/pics/screen.png')
result = cli.analyse_with_object(target_object, 'wechat_logo.png')
print(result)
```

用法基本与path类一致。

### 多目标支持

你可以在一次请求内检测多个目标。

```python
result = cli.analyse_with_path('screen.png', ['wechat_logo.png', 'app_store_logo.png'])
print(result)
```

## 协议

[MIT](LICENSE)
