import math

from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Here are some brittle values which need changed if associated values in prod
# code change.
# ... but the same goes for every ID in this test.
full_slider_value = 100000
slider_step = 100
full_withdrawal_string = "You are withdrawing the full amount. ✔️"
partial_withdrawal_string = \
    ("You are not withdrawing the full amount.<br>  "
     "Move the sliders until they add up to $100,000.")
# HTML matching works if the style attribute is surrounding in double quotes
# instead of single.
optimal_tax_string = \
    ('You are paying the lowest possible income tax on your $100,000 '
     'withdrawal.  <div style="font-size: 25px">You Win!✔️</div>')
suboptimal_tax_string = \
    ("You are paying more income tax than you have to.  "
     "Play with the sliders!")


class WithdrawalMessage(Enum):
    FULL_WITHDRAWAL = 1
    PARTIAL_WITHDRAWAL = 2
    UNKNOWN = 3


class OptimalTaxMessage(Enum):
    OPTIMAL_TAX = 1
    SUBOPTIMAL_TAX = 2
    EMPTY = 3
    UNKNOWN = 4

# Some utility methods that are not tests themselves


def convert_bucket_withdrawal_element_to_int(withdrawal_element):
    return int(withdrawal_element
               .get_attribute("value")
               .replace("Withdrawal: $", "")
               .replace(",", ""))


def convert_bucket_tax_element_to_int(tax_element):
    return int(tax_element
               .get_attribute("value")
               .replace("Tax: $", "")
               .replace(",", ""))


def convert_total_tax_element_to_int(total_tax_element):
    return int(total_tax_element
               .get_attribute("value")
               .replace("$", "")
               .replace(",", ""))


def get_full_withdrawal_message_state(withdrawal_message_element):
    withdrawal_message_element_value = \
        withdrawal_message_element.get_attribute("innerHTML")
    if withdrawal_message_element_value == full_withdrawal_string:
        return WithdrawalMessage.FULL_WITHDRAWAL
    elif withdrawal_message_element_value == partial_withdrawal_string:
        return WithdrawalMessage.PARTIAL_WITHDRAWAL
    else:
        return WithdrawalMessage.UNKNOWN


def get_optimal_tax_message_state(optimal_tax_message_element):
    optimal_tax_message_element_value = \
        optimal_tax_message_element.get_attribute("innerHTML")
    if optimal_tax_message_element_value == optimal_tax_string:
        return OptimalTaxMessage.OPTIMAL_TAX
    elif optimal_tax_message_element_value == suboptimal_tax_string:
        return OptimalTaxMessage.SUBOPTIMAL_TAX
    elif optimal_tax_message_element_value == "":
        return OptimalTaxMessage.EMPTY
    else:
        return OptimalTaxMessage.UNKNOWN


def setup_function(function):
    # Setup code, runs before each test
    global driver
    driver = webdriver.Chrome()

    # Only works in my Windows dev environment.  Replace with your own path.
    # Maybe one day I'll set up a proper system property
    # By running locally, I haven't run into timing issues yet.  I may need to
    # do something about that if I want to test against a host on the other
    # side of the internet.
    driver.get("file:///C:/Drawdown/exercise1.html")


def teardown_function(function):
    # Teardown code, runs after each test
    driver.quit()


def test_change_withdrawal_via_input_test():

    # First, clear (which becomes $0), then enter text.
    year_1_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-0")
    year_1_withdrawal_text.clear()
    # The following actually yields "$030000" in the input box (harmlessly).
    year_1_withdrawal_text.send_keys("30000")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$30,000"

    # Now try using Ctrl-A, to clear fully upon first character of keyboard
    # input.
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("10000")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$10,000"

    # Handle input with different formats.
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("5,000")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$5,000"
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("$8000")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$8,000"
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("$10,000")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$10,000"

    # Verify that invalid inputs turn into $0.
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("-17")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$0"
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys("fklj")
    year_1_withdrawal_text.send_keys(Keys.RETURN)
    assert year_1_withdrawal_text.get_attribute("value") == "$0"

    # Try with the second slider.
    year_2_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-1")
    year_2_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_2_withdrawal_text.send_keys("10000")
    year_2_withdrawal_text.send_keys(Keys.RETURN)
    assert year_2_withdrawal_text.get_attribute("value") == "$10,000"

    # At this point, year 1 is 0 and year 2 is 10000, so year 3 cannot be more
    # than 90000.
    year_3_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-2")
    year_3_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_3_withdrawal_text.send_keys("99000")
    year_3_withdrawal_text.send_keys(Keys.RETURN)
    assert year_3_withdrawal_text.get_attribute("value") == "$90,000"


def test_changing_input_text_changes_slider():
    # Minus 4 because of borders
    full_slider_height = driver.find_element(
        by=By.ID, value="slider-vertical-0").size['height'] - 2

    new_slider_value = 20000

    year_1_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-0")

    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys(new_slider_value)
    year_1_withdrawal_text.send_keys(Keys.RETURN)

    # Verify correct height for the image tiled over the filled potion of the
    # slider.
    year_1_withdrawal_slider_image = driver.find_element(
        by=By.ID, value="slider-filled-0")
    actual_height = year_1_withdrawal_slider_image.size['height']
    expected_height = math.floor(
        full_slider_height * new_slider_value / 100000)
    assert actual_height == expected_height

    # Verify correct position for the slider handle
    year_1_withdrawal_handle = driver.find_element(
        by=By.XPATH, value="//div[@id='slider-vertical-0']/span")
    handle_style = year_1_withdrawal_handle.get_attribute("style")
    actual_handle_position = -1
    for style in handle_style.split(';'):
        if 'bottom' in style:
            actual_handle_position = style.split(':')[1].strip()
            break

    expected_handle_position = "%s%%" % round(
        new_slider_value / full_slider_value * 100)
    assert actual_height == expected_height


def test_changing_slider_changes_input_text():
    year_3_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-2")
    year_3_withdrawal_initial_value = int(year_3_withdrawal_text
                                          .get_attribute("value")
                                          .replace(',', '')
                                          .replace('$', ''))

    year_3_withdrawal_handle = driver.find_element(
        by=By.XPATH, value="//div[@id='slider-vertical-2']/span")
    year_3_withdrawal_handle.click()
    year_3_withdrawal_handle.send_keys(Keys.DOWN)

    year_3_withdrawal_final_value = int(year_3_withdrawal_text
                                        .get_attribute("value")
                                        .replace(',', '')
                                        .replace('$', ''))

    assert year_3_withdrawal_final_value == (
        year_3_withdrawal_initial_value - slider_step
    )


def test_bucket_fill_levels():
    size_of_zero_bucket = 29200 * 3
    size_of_ten_bucket = 23200 * 3
    size_of_twelve_bucket = 71100 * 3
    bucket_container_height = 98  # 100, - 2 for borders

    year_1_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-0")
    year_2_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-1")
    year_3_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-2")
    year_1_withdrawal_text.clear()
    year_2_withdrawal_text.clear()
    year_3_withdrawal_text.clear()

    year_1_withdrawal_text.click()
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys('70000')
    year_2_withdrawal_text.click()
    year_2_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_2_withdrawal_text.send_keys('15000')
    year_3_withdrawal_text.click()
    year_3_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_3_withdrawal_text.send_keys('15000')
    year_3_withdrawal_text.send_keys(Keys.RETURN)

    zero_percent_bucket = driver.find_element(
        by=By.ID, value="zero-percent-bucket")
    ten_percent_bucket = driver.find_element(
        by=By.ID, value="ten-percent-bucket")
    twelve_percent_bucket = driver.find_element(
        by=By.ID, value="twelve-percent-bucket")

    # Zero percent bucket has 29200 + 15000 + 15000 = 59200 in it.
    expected_zero_bucket_height = round(
        59200 * bucket_container_height / size_of_zero_bucket)
    # Ten percent bucket has 23200 in it, the size of the ten percent bracket
    # for the single year where this example hits it (year 1, 70000).
    expected_ten_bucket_height = round(
        23200 * bucket_container_height / size_of_ten_bucket)
    # Twelve percent bucket has 70000 - 29200 - 23200 = 27600 in it.
    expected_twelve_bucket_height = round(
        17600 * bucket_container_height / size_of_twelve_bucket)

    assert zero_percent_bucket.size['height'] == expected_zero_bucket_height
    assert ten_percent_bucket.size['height'] == expected_ten_bucket_height
    assert twelve_percent_bucket.size['height'] == (
        expected_twelve_bucket_height
    )


# We'll use this one for a few different cases.
def subtest_math_and_messaging(
        year_1_withdrawal,
        year_2_withdrawal,
        year_3_withdrawal,
        expected_0_bucket_withdrawal,
        expected_10_bucket_withdrawal,
        expected_12_bucket_withdrawal,
        expected_0_bucket_tax,
        expected_10_bucket_tax,
        expected_12_bucket_tax,
        expected_overall_tax,
        expected_withdrawal_message,
        expected_optimal_tax_message):
    year_1_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-0")
    year_2_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-1")
    year_3_withdrawal_text = driver.find_element(
        by=By.ID, value="slider-value-2")

    bucket_0_value = driver.find_element(by=By.ID, value="zero-percent-value")
    bucket_0_tax = driver.find_element(by=By.ID, value="zero-percent-tax")
    bucket_10_value = driver.find_element(by=By.ID, value="ten-percent-value")
    bucket_10_tax = driver.find_element(by=By.ID, value="ten-percent-tax")
    bucket_12_value = driver.find_element(
        by=By.ID, value="twelve-percent-value")
    bucket_12_tax = driver.find_element(by=By.ID, value="twelve-percent-tax")

    total_tax = driver.find_element(by=By.ID, value="total-tax")

    full_withdrawal_or_not = driver.find_element(
        by=By.ID, value="full-withdrawal-or-not")
    min_tax_or_not = driver.find_element(by=By.ID, value="min-tax-or-not")

    # Clear all three before adding values so we don't run into max value
    # restrictions for some valid combinations of withdrawals.
    year_1_withdrawal_text.clear()
    year_2_withdrawal_text.clear()
    year_3_withdrawal_text.clear()

    year_1_withdrawal_text.click()
    year_1_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_1_withdrawal_text.send_keys(year_1_withdrawal)
    year_2_withdrawal_text.click()
    year_2_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_2_withdrawal_text.send_keys(year_2_withdrawal)
    year_3_withdrawal_text.click()
    year_3_withdrawal_text.send_keys(Keys.CONTROL + 'a')
    year_3_withdrawal_text.send_keys(year_3_withdrawal)
    year_3_withdrawal_text.send_keys(Keys.RETURN)

    # Check that the resulting tax buckets are correct.
    assert convert_bucket_withdrawal_element_to_int(bucket_0_value) == (
        expected_0_bucket_withdrawal
    )
    assert convert_bucket_withdrawal_element_to_int(bucket_10_value) == (
        expected_10_bucket_withdrawal
    )
    assert convert_bucket_withdrawal_element_to_int(bucket_12_value) == (
        expected_12_bucket_withdrawal
    )

    # Check that the resulting tax amounts are correct.
    assert convert_bucket_tax_element_to_int(bucket_0_tax) == (
        expected_0_bucket_tax
    )
    assert convert_bucket_tax_element_to_int(bucket_10_tax) == (
        expected_10_bucket_tax
    )
    assert convert_bucket_tax_element_to_int(bucket_12_tax) == (
        expected_12_bucket_tax
    )

    # Check that the overall tax amount is correct.
    assert convert_total_tax_element_to_int(total_tax) == expected_overall_tax

    # Check whether the appropriate withdrawal message and optimal-or-not tax
    # message is displayed.
    assert get_full_withdrawal_message_state(
        full_withdrawal_or_not) == expected_withdrawal_message
    assert get_optimal_tax_message_state(
        min_tax_or_not) == expected_optimal_tax_message


def test_math_on_min_tax_case():
    subtest_math_and_messaging(
        year_1_withdrawal="30000",
        year_2_withdrawal="30000",
        year_3_withdrawal="40000",
        expected_0_bucket_withdrawal=87600,
        expected_10_bucket_withdrawal=12400,
        expected_12_bucket_withdrawal=0,
        expected_0_bucket_tax=0,
        expected_10_bucket_tax=1240,
        expected_12_bucket_tax=0,
        expected_overall_tax=1240,
        expected_withdrawal_message=WithdrawalMessage.FULL_WITHDRAWAL,
        expected_optimal_tax_message=OptimalTaxMessage.OPTIMAL_TAX
    )


def test_math_on_max_tax_case():
    subtest_math_and_messaging(
        year_1_withdrawal="100000",
        year_2_withdrawal="0",
        year_3_withdrawal="0",
        expected_0_bucket_withdrawal=29200,
        expected_10_bucket_withdrawal=23200,
        expected_12_bucket_withdrawal=47600,
        expected_0_bucket_tax=0,
        expected_10_bucket_tax=2320,
        expected_12_bucket_tax=5712,
        expected_overall_tax=8032,
        expected_withdrawal_message=WithdrawalMessage.FULL_WITHDRAWAL,
        expected_optimal_tax_message=OptimalTaxMessage.SUBOPTIMAL_TAX
    )


def test_incomplete_withdrawal():
    subtest_math_and_messaging(
        year_1_withdrawal="29200",
        year_2_withdrawal="29200",
        year_3_withdrawal="0",
        expected_0_bucket_withdrawal=58400,
        expected_10_bucket_withdrawal=0,
        expected_12_bucket_withdrawal=0,
        expected_0_bucket_tax=0,
        expected_10_bucket_tax=0,
        expected_12_bucket_tax=0,
        expected_overall_tax=0,
        expected_withdrawal_message=WithdrawalMessage.PARTIAL_WITHDRAWAL,
        expected_optimal_tax_message=OptimalTaxMessage.EMPTY
    )
