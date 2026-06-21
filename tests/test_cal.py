from app.cal import add


def test_add():
    assert add(1, 1) == 2
    assert add(1, 2) == 3


def main():
    test_add()


if __name__ == "__main__":
    main()
