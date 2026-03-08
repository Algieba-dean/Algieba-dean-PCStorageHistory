from my_package.main import main


def test_smoke() -> None:
    assert "delete" in main()
