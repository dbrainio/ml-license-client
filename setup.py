from setuptools import setup


packages = {
    'license_client': 'license_client/'
}

setup(
    name='license_client',
    version='0.3.0',
    author='Dbrain',
    author_email='',
    license='',
    description='Client of Dbrain License Service',
    packages=packages,
    package_dir=packages,
    include_package_data=False,
    install_requires=[
        'pycryptodome==3.9.8',
        'aiohttp>=3.5.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
