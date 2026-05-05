from neurocartographer.connectors.dandi import parse_asset_payload


def test_parse_dandi_asset_payload_extracts_nwb_paths_sizes_and_urls():
    payload = {
        "results": [
            {
                "asset_id": "asset-1",
                "path": "sub-01/sub-01_ses-1_ophys.nwb",
                "size": 12345,
                "download_url": "https://api.dandiarchive.org/api/assets/asset-1/download/",
            },
            {
                "identifier": "asset-2",
                "path": "README.txt",
                "blob": {"size": 321},
            },
        ]
    }

    assets = parse_asset_payload(payload)

    assert assets[0].path == "sub-01/sub-01_ses-1_ophys.nwb"
    assert assets[0].size_bytes == 12345
    assert assets[0].url == "https://api.dandiarchive.org/api/assets/asset-1/download/"
    assert assets[0].standard == "NWB"
    assert assets[1].size_bytes == 321
    assert assets[1].standard == "unknown"
