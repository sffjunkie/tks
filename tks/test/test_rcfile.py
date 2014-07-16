import tempfile

from tks.rc import rcfile

def test_rcfile_init():
    f = rcfile()

    assert f.parser is None


def test_rcfile_default_config():
    f = rcfile()
    f.read()

    assert f.has_section('font')
    assert f.has_section('color')


def test_rcfile_getitem():
    f = rcfile()
    f.reads(u"[font]\nfamily=Consolas")

    assert f['font.family'] == 'Consolas'


def test_rcfile_getsubitem():
    f = rcfile()
    f.reads(u"[font]\ntext.family=Consolas")

    assert f['font.text.family'] == 'Consolas'


def test_rcfile_setitem():
    f = rcfile()
    f['font.family'] = 'Consolas'

    assert f['font.family'] == 'Consolas'


def test_rcfile_write():
    f = rcfile()
    f['font.family'] = 'Consolas'
    fname = tempfile.mktemp()
    f.write(fname)

    f2 = rcfile(fname)
    f2.read()

    assert f2['font.family'] == 'Consolas'
