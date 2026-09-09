from execution_finality import EFCode

def test_failure_code_catalog_is_unique_and_expected_size():
    vals=[x.value for x in EFCode]
    assert len(vals)==len(set(vals))
    assert len(vals)==25
