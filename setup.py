from setuptools import setup, find_packages


setup(
    name='findit_client',
    version='0.1.2',
    description='client for findit, with no opencv needed',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit_client',
    packages=find_packages(),
    install_requires=[
        'requests',
        'logzero',
    ]
)
