from setuptools import setup, find_packages

setup(
    name='compdfkit-api-python',
    version='0.0.1',
    description='Python SDK for compdfkit API',
    author='PDF Technologies, Inc.',
    author_email='support@compdf.com',
    url='https://api.compdf.com/api-reference/overview',
    packages=find_packages(),
    install_requires=['requests', 'requests_toolbelt'],
    license='MIT',
    python_requires='>=3.8',
)
