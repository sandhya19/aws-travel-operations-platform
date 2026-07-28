"""Repository scaffold checks."""


def test_package_can_be_imported() -> None:
    """Keep the package boundary valid before application code is introduced."""
    import travel_operations

    assert travel_operations.__doc__ is not None
