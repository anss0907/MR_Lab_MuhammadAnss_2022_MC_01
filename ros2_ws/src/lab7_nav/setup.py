from setuptools import find_packages, setup

package_name = 'lab7_nav'

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
            'goal_recorder = lab7_nav.goal_recorder:main',
            'waypoint_navigator_step_5 = lab7_nav.waypoint_navigator_step_5:main',
            'waypoint_navigator_Task2 = lab7_nav.waypoint_navigator_Task2:main',
            'waypoint_navigator_Task3 = lab7_nav.waypoint_navigator_Task3:main'
        ],
    },
)
