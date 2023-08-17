from setuptools import setup, find_packages

setup(
    name='AntebeotCli',
    version='0.1',
    packages=find_packages(),
    package_data={
        '': ['*.txt', '*.md'],
    },
    install_requires=[
        'json',
        'requests',
        'hashlib'
    ],
    entry_points={
        'console_scripts': [
            #'my-script-name = my_package.my_module:my_function',
        ],
    },
)
