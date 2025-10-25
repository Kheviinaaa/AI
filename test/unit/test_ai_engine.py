import json, os, glob

def test_output_file():
    # Find file automatically
    files = glob.glob("**/sample_output.json", recursive=True)
    assert files, "sample_output.json missing in project"
    path = files[0]

    with open(path) as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert "UserStories" in data[0]
    assert "TestCases" in data[0]
