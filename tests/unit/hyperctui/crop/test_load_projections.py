"""Contract tests for Crop.load_projections ahead of the NeuNorm removal (issue #175).

These run against the pinned NeuNorm 1.6.12 and pin every behavior the
replacement loader must preserve (audit 2026-06-11): float32 output dtype,
singleton-3D FITS squeezing, auto gamma filtering of saturated integer
pixels, the positional 0/180-degree mapping that follows list_projections
order, mean_image/image_size/crop_live_image side effects, and the
CropError on a missing _SummedImg.fits.
"""

import numpy as np
import pytest
from astropy.io import fits

from hyperctui.crop.crop import Crop
from hyperctui.session import SessionKeys
from hyperctui.utilities.exceptions import CropError
from hyperctui.utilities.file_utilities import get_list_img_files_from_top_folders


class _ParentStub:
    """Minimal stand-in for the main window: only what load_projections touches."""

    def __init__(self, list_projections):
        self.session_dict = {SessionKeys.list_projections: list_projections}


def _write_summed_fits(projection_dir, image, run="Run_0001", stem="frame"):
    run_dir = projection_dir / run
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"{stem}_SummedImg.fits"
    fits.HDUList([fits.PrimaryHDU(image)]).writeto(str(path))
    return path


@pytest.fixture
def projection_pair(tmp_path):
    """Two projection folders (0 and 180 degrees) with distinguishable images.

    Corner markers make orientation or identity mix-ups fail loudly.
    """
    img_0 = np.full((16, 16), 100.0, dtype=np.float32)
    img_0[1, 2] = 7.0
    img_180 = np.full((16, 16), 200.0, dtype=np.float32)
    img_180[2, 1] = 9.0

    dir_0 = tmp_path / "proj_000deg"
    dir_180 = tmp_path / "proj_180deg"
    _write_summed_fits(dir_0, img_0)
    _write_summed_fits(dir_180, img_180)
    return {
        "dirs": [str(dir_0), str(dir_180)],
        "img_0": img_0,
        "img_180": img_180,
    }


class TestLoadProjectionsContract:
    def test_outputs_and_side_effects(self, projection_pair):
        """pixel values, dtype, image_size, mean and live image all pinned"""
        parent = _ParentStub(projection_pair["dirs"])
        crop = Crop(parent=parent)
        crop.load_projections()

        np.testing.assert_array_equal(np.asarray(parent.image_0_degree), projection_pair["img_0"])
        np.testing.assert_array_equal(np.asarray(parent.image_180_degree), projection_pair["img_180"])
        # empirically pinned 1.x dtype contract: INTEGER FITS input is cast
        # to native float32 by the gamma filter, but FLOAT input passes
        # through raw — here big-endian '>f4' (the gamma filter's cast only
        # runs for integer dtypes; float takes its warning path untouched).
        # The replacement loader will normalize everything to NATIVE float32
        # (float32-precision values identical) — relax only the byte order.
        loaded_dtype = np.asarray(parent.image_0_degree).dtype
        assert loaded_dtype.newbyteorder("=") == np.float32
        assert parent.image_size == {"height": 16, "width": 16}

        expected_mean = (projection_pair["img_0"] + projection_pair["img_180"]) / 2.0
        np.testing.assert_allclose(crop.mean_image, expected_mean, rtol=1e-6)
        np.testing.assert_array_equal(parent.crop_live_image, crop.mean_image)

    def test_angular_identity_follows_list_order(self, projection_pair):
        """0/180-degree identity is encoded ONLY by list position (audit H1):
        reversing list_projections swaps the assignment. A replacement
        loader must iterate the list exactly as given — never sort or
        re-glob."""
        parent = _ParentStub(list(reversed(projection_pair["dirs"])))
        crop = Crop(parent=parent)
        crop.load_projections()

        np.testing.assert_array_equal(np.asarray(parent.image_0_degree), projection_pair["img_180"])
        np.testing.assert_array_equal(np.asarray(parent.image_180_degree), projection_pair["img_0"])

    def test_singleton_3d_fits_is_squeezed(self, tmp_path):
        """(1, H, W) FITS HDUs occur on this instrument (the preview code
        reshapes them too); NeuNorm 1.x collapses them to 2D on load"""
        img = np.arange(16 * 16, dtype=np.float64).reshape(1, 16, 16)
        dir_a = tmp_path / "proj_a"
        dir_b = tmp_path / "proj_b"
        _write_summed_fits(dir_a, img)
        _write_summed_fits(dir_b, img)

        parent = _ParentStub([str(dir_a), str(dir_b)])
        crop = Crop(parent=parent)
        crop.load_projections()

        assert np.asarray(parent.image_0_degree).shape == (16, 16)
        assert parent.image_size == {"height": 16, "width": 16}
        np.testing.assert_array_equal(np.asarray(parent.image_0_degree), img[0].astype(np.float32))

    def test_saturated_uint16_pixel_is_neighbor_averaged(self, tmp_path):
        """characterization of NeuNorm 1.x's auto gamma filter: integer
        pixels above iinfo(dtype).max - 5 are replaced by the 8-neighbor
        mean. The port must either replicate this (NIS has the reference
        implementation) or document dropping it after checking real
        *_SummedImg.fits dtypes — this test is the tripwire either way."""
        img = np.full((16, 16), 100, dtype=np.uint16)
        img[5, 5] = 65535
        dir_a = tmp_path / "proj_a"
        dir_b = tmp_path / "proj_b"
        _write_summed_fits(dir_a, img)
        _write_summed_fits(dir_b, img)

        parent = _ParentStub([str(dir_a), str(dir_b)])
        crop = Crop(parent=parent)
        crop.load_projections()

        loaded = np.asarray(parent.image_0_degree)
        assert loaded[5, 5] == pytest.approx(100.0), "saturated pixel should be neighbor-averaged, not 65535"
        assert loaded[0, 0] == pytest.approx(100.0)

    def test_missing_summed_img_raises_croperror(self, tmp_path):
        """a Run_* folder without *_SummedImg.fits must surface as CropError"""
        dir_a = tmp_path / "proj_a"
        (dir_a / "Run_0001").mkdir(parents=True)

        parent = _ParentStub([str(dir_a)])
        crop = Crop(parent=parent)
        with pytest.raises(CropError):
            crop.load_projections()


class TestGetListImgFilesFromTopFolders:
    def test_preserves_input_order(self, tmp_path):
        """the angular-identity contract upstream: output order == input order"""
        paths = []
        for name in ("zzz_first", "aaa_second", "mmm_third"):
            d = tmp_path / name
            paths.append((str(d), str(_write_summed_fits(d, np.zeros((4, 4), dtype=np.float32)))))

        result = get_list_img_files_from_top_folders([p for p, _ in paths])
        assert result == [f for _, f in paths], "must follow input order, not sorted order"

    def test_projection_without_run_folder_is_silently_skipped(self, tmp_path):
        """characterization (audit M finding): a projection folder with no
        Run_* subfolder is dropped without error, shortening the list —
        downstream positional indexing then mis-assigns 0/180. Pinned here
        so any fix is a conscious contract change."""
        d_ok = tmp_path / "with_run"
        f_ok = _write_summed_fits(d_ok, np.zeros((4, 4), dtype=np.float32))
        d_empty = tmp_path / "no_run"
        d_empty.mkdir()

        result = get_list_img_files_from_top_folders([str(d_empty), str(d_ok)])
        assert result == [str(f_ok)]
