from unittest.mock import MagicMock, patch

import numpy as np

from backend.services.landcover_zonal import compute_landcover_zonal


def test_compute_landcover_zonal_returns_percentages():
    mock_data = np.array(
        [
            [
                [10, 10, 20, 20, 30],
                [10, 10, 20, 20, 30],
                [40, 40, 50, 50, 60],
                [40, 40, 50, 50, 60],
                [40, 40, 50, 50, 60],
            ]
        ],
        dtype=np.uint8,
    )

    coords = [
        [
            [-46.64, -23.54],
            [-46.62, -23.54],
            [-46.62, -23.56],
            [-46.64, -23.56],
            [-46.64, -23.54],
        ]
    ]

    with patch("backend.services.landcover_zonal.rasterio.open") as mock_open:
        mock_dataset = MagicMock()
        mock_dataset.read.return_value = mock_data
        mock_dataset.height = 5
        mock_dataset.width = 5
        mock_dataset.__enter__ = MagicMock(return_value=mock_dataset)
        mock_dataset.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_dataset

        with patch(
            "backend.services.landcover_zonal.geometry_mask",
            return_value=np.ones((5, 5), dtype=bool),
        ):
            result = compute_landcover_zonal(coords, "/mock/tile.tif")

    assert "classes" in result
    assert "total_pixels" in result
    assert result["total_pixels"] > 0
    assert isinstance(result["classes"], list)


def test_compute_landcover_zonal_handles_no_data():
    coords = [
        [
            [-46.64, -23.54],
            [-46.62, -23.54],
            [-46.62, -23.56],
            [-46.64, -23.56],
            [-46.64, -23.54],
        ]
    ]

    with patch("backend.services.landcover_zonal.rasterio.open") as mock_open:
        mock_dataset = MagicMock()
        mock_dataset.read.return_value = np.zeros((1, 5, 5), dtype=np.uint8)
        mock_dataset.height = 5
        mock_dataset.width = 5
        mock_dataset.__enter__ = MagicMock(return_value=mock_dataset)
        mock_dataset.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_dataset

        with patch(
            "backend.services.landcover_zonal.geometry_mask",
            return_value=np.ones((5, 5), dtype=bool),
        ):
            result = compute_landcover_zonal(coords, "/mock/tile.tif")

    assert "total_pixels" in result
