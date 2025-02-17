from setuptools import find_packages, setup

setup(
    name='based-random',
    version='0.1.1',    
    description='Generates a random number based on the unit-type of the based.cooking website',
    url='https://github.com/Giftzwerg02/based-random',
    author='Giftzwerg02',
    license='MIT',
    packages=find_packages(exclude=['based_random.internal']),
    py_modules=['based_random'],
    install_requires=['requests',
                      'beautifulsoup4',                     
                      ],

    classifiers=[
    ],
)

