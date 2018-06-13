from setuptools import find_packages, setup

REQUIRED_PACKAGES = ['Keras>=2.0.4', 'h5py>=2.7.0', 'numpy', 'json']

setup(
    name='trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='ECG Trainer'
    )