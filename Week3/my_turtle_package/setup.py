from setuptools import find_packages, setup

package_name = 'my_turtle_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='anss0907',
    maintainer_email='muhammadanss0907@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'my_node = my_turtle_package.my_node:main',
            'move_turtle = my_turtle_package.move_turtle:main',
            'move_patterns_node = my_turtle_package.move_patterns_node:main',
            'multi_turtle_node = my_turtle_package.multi_turtle_node:main',
            'go_to_goal_node = my_turtle_package.go_to_goal_node:main',
        ],
    },
)
