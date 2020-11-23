from setuptools import setup


packages = {
    'license_client': 'license_client/'
}

setup(
    name='license_client',
    version='0.1.0',
    author='Dbrain',
    author_email='',
    license='',
    description='',
    packages=packages,
    package_dir=packages,
    include_package_data=False,
    install_requires=[
        'pycryptodome==3.9.9', 'aiohttp==3.6.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
