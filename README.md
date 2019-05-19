# findit-client

[![image](https://img.shields.io/pypi/pyversions/requests.svg)](https://pypi.org/project/requests/)
[![Build Status](https://travis-ci.org/williamfzc/findit-client.svg?branch=master)](https://travis-ci.org/williamfzc/findit-client)

Client for [findit](https://github.com/williamfzc/findit), with no opencv needed.

## 目的

- 旨在提供超低依赖的findit client，用于适应不同机器（尤其是无法安装opencv）的环境。
- 该client只依赖于http请求，只使用了requests，依赖环境与requests一致。

## 使用

我们希望在本地图片 `screen.png` 中寻找 `wechat_logo.png`

### 本地服务

假设你的findit-server部署在 29412 端口

```python
cli = FindItClient(port=29412)
assert cli.heartbeat()
result = cli.analyse_with_path('screen.png', u'wechat_logo.png')
print(result)
```

result结果：

```text
{'data': {'temp_template': {'FeatureEngine': [524.6688232421875, 364.54248046875], 'TemplateEngine': [505.5, 374.5]}}, 'target_name': 'temp_target', 'target_path': '/tmp/tmp0k8dfeez.png'}
```

### 远程服务

假设你的findit-server部署在远程服务器 172.17.12.34 的 29412 端口

```python
cli = FindItClient(host='172.17.12.34', port=29412)
assert cli.heartbeat()
result = cli.analyse_with_path('screen.png', u'wechat_logo.png')
print(result)
```

## 协议

[MIT](LICENSE)
