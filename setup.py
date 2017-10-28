from setuptools import setup


setup(
    name='data-science-apis-example',
    packages=['dsapi'],
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'rq',
        'redis',
        'numpy',
        'scipy',
        'pandas',
        'scikit-learn',
        'gunicorn'
    ]
)
