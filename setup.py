#  -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
from billtracker.version import __version__

setup(
	name='billtracker',
	version=__version__,
	packages=find_packages(),
	url='https://github.com/codycuellar/bill_tracker',
	license='© Cody Cuellar',
	author='Cody Cuellar',
	author_email='cody.cuellar@gmail.com',
	description='A simple bill tracking and notification system.',
	platforms=['MacOS 10.10', 'MacOS 10.11', 'MacOS 10.12'],
	python_requires='>=2.7',
	install_requires=[],
	dependency_links=[],
	entry_points={
		'console_scripts': ['notify=billtracker.notify:startup',
							'pay=billtracker.pay_bills:startup'],
		}
	)
