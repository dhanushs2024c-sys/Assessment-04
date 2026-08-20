from DigitalWallet import DigitalWallet


def test_suspicious_transaction():
    wallet = DigitalWallet()
    wallet.create_account("A1", "Test", "1234", 100000)

    fraud, reasons = wallet.check_fraud("A1", 90000)

    assert fraud

    print("Suspicious transaction: PASS")


def test_duplicate_account():
    wallet = DigitalWallet()

    wallet.create_account("A1", "Test", "1234", 10000)

    result, message = wallet.create_account(
        "A1", "Test2", "5678", 5000
    )

    assert not result

    print("Duplicate account: PASS")


def test_negative_amount():
    wallet = DigitalWallet()
    wallet.create_account("A1", "Test", "1234", 10000)

    result, message = wallet.deposit("A1", -100)

    assert not result

    print("Negative amount: PASS")


def test_money_transfer():
    wallet = DigitalWallet()

    wallet.create_account("A1", "Test1", "1234", 10000)
    wallet.create_account("A2", "Test2", "5678", 5000)

    result, message = wallet.transfer("A1", "A2", 2000)

    assert result
    assert wallet.get_balance("A1") == 8000
    assert wallet.get_balance("A2") == 7000

    print("Money transfer: PASS")


def main():

    print("================================")
    print("DIGITAL WALLET QA")
    print("================================")

    test_normal_transaction()
    test_insufficient_balance()
    test_daily_limit()
    test_multiple_failed_pins()
    test_suspicious_transaction()
    test_duplicate_account()
    test_negative_amount()
    test_money_transfer()

    print("================================")
    print("ALL DIGITAL WALLET TESTS PASSED")
    print("================================")


if __name__ == "__main__":
    main()
