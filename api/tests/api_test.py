import pytest
import tempfile
import os


def _data_file(filename):
    import os.path
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)


@pytest.fixture()
def cleandir():
    return tempfile.mkdtemp()


@pytest.mark.usefixtures("cleandir")
class TestApi(object):
    def test_framework(self):
        assert 1 == 1

    def test_small(self):
        from blob_api import blob_api
        assert blob_api.small() == 4

    def test_sha_sum(self):
        from blob_api import blob_api
        shasum = blob_api.sha1_of_file(_data_file('test_file'))

        assert shasum == '1979403866ee76fe918ad584a789e125da04863d'

    def test_we_get_correct_prefix_from_checksum(self):
        from blob_api import blob_api
        prefix = blob_api.prefix_from_sum('1979403866ee76fe918ad584a789e125da04863d')

        assert prefix == '19/79'

    def test_prep_dirs(self, cleandir):
        from blob_api import blob_api

        blob_api.make_store_dirs(cleandir, '19/79')
        exists = os.path.exists(os.path.join(cleandir, '19/79'))

        assert exists == True
