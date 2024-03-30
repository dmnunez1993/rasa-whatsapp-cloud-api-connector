from setuptools import setup, find_packages

install_requires = [
    'rasa==3.6.16',
    'rasa-sdk==3.6.2',
    'requests==2.31.0',
]

setup(
    name='rasa_whatsapp_connector',
    version='0.0.1',
    package_dir={'': 'src'},
    install_requires=install_requires,
    packages=find_packages(),
)
