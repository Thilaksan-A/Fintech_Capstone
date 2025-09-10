from app.utils import compose_filters


def test_compose_filters_basic():
    # Simple filters for demonstration
    def filter_even(nums):
        return (n for n in nums if n % 2 == 0)

    def filter_gt_two(nums):
        return (n for n in nums if n > 2)

    composed = compose_filters(filter_even, filter_gt_two)
    data = [1, 2, 3, 4, 5, 6]
    result = list(composed(data))
    assert result == [4, 6]


def test_compose_filters_no_filters():
    data = [1, 2, 3]
    composed = compose_filters()
    result = list(composed(data))
    assert result == [1, 2, 3]


def test_compose_filters_single_filter():
    def filter_odd(nums):
        return (n for n in nums if n % 2 == 1)

    composed = compose_filters(filter_odd)
    data = [1, 2, 3, 4]
    result = list(composed(data))
    assert result == [1, 3]
