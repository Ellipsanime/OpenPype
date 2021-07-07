import pytest
import openpype.modules.shotgrid.lib.credentials as sut


@pytest.mark.xfail(raises=Exception)
def test_missing_shotgrid_url():
    # arrange
    url = ""
    # act
    sut.get_shotgrid_hostname(url)
    # assert
