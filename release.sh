rm -rf dist
rm -rf django_haystackbrowser.egg-info
rm -rf docs/_build
python setup.py clean

python setup.py --long-description | rst2html.py --halt=3 > /dev/null
[ $? -ne 0 ] && exit;

python setup.py sdist --formats=tar,gztar,bztar,zip
python setup.py check
