from setuptools import setup
from codecs import open


with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name="systemd-stopper",
    packages=['systemd_stopper'],
    version="0.1.0",
    author="Christoph Schmitt",
    author_email="dev@chschmitt.de",
    description="A signal handler utility for Python applications running as systemd units",
    long_description=readme,
    license="BSD License",
    package_data={'': ['LICENSE']},
    include_package_data=True,
    keywords="systemd linux signal-handling",
    url="https://github.com/chschmitt/systemd-stopper",
    package_dir={'systemd_stopper': 'systemd_stopper'},
    # test_suite="tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: POSIX :: Linux"
    ]
)