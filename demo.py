# -*- coding: utf-8 -*-

"""
Webdriver Python bindings demo
2017 samuels(c)
"""
import logging
from logging import handlers

import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = None


class TestException(RuntimeError):
    pass


def init_logger():
    global logger
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = handlers.RotatingFileHandler('debug.log')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)


def wait_for_id(driver, delay, id_to_wait):
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, id_to_wait)))
        logger.info("Element {0} is ready!".format(id_to_wait))
    except TimeoutException:
        raise TestException("Waiting for {0} timed out!".format(id_to_wait))


def wait_for_class(driver, delay, class_to_wait):
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, class_to_wait)))
        logger.info("Element {0} is ready!".format(class_to_wait))
    except TimeoutException:
        raise TestException("Waiting for {0} timed out!".format(class_to_wait))


def wait_for_selector(driver, delay, selector_to_wait):
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_to_wait)))
        logger.info("Element {0} is ready!".format(selector_to_wait))
    except TimeoutException:
        raise TestException("Waiting for {0} timed out!".format(selector_to_wait))


def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    logger.info("WebDriver init successful")
    return driver


def open_page(driver, page, id_to_wait):
    if not id_to_wait:
        raise TestException("Test Failed! No ID was specified.")
    delay = 30
    driver.get(page)
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, id_to_wait)))
        logger.info("Page {0} is ready!".format(page))
    except TimeoutException:
        logger.error("Test Fail! Loading took too much time!")
        raise TestException("Timeout error")


def main():
    global logger
    init_logger()
    driver = init_driver()
    open_page(driver, 'http://globale:globalelocal@anna.bglobale.de', 'globale_popup')
    driver.find_element_by_css_selector('.backToShop').click()
    try:
        wait_for_id(driver, 10, 'globale_popup')
    except (TimeoutException, TestException):
        logger.info("Intro popup closed")
        pass
    driver.find_element_by_css_selector('#shippingSwitcherLink').click()
    logger.info("Shipping popup opened")
    select = Select(driver.find_element_by_id('gle_selectedCountry'))
    logger.info("Selected country: {0}".format(select.first_selected_option.text))
    if select.first_selected_option.text != "ISRAEL":
        raise TestException("Bad country selector Value!")
    select = Select(driver.find_element_by_id('gle_selectedCurrency'))
    logger.info("Selected currency: {0}".format(select.first_selected_option.text))
    if select.first_selected_option.text != "ISRAELI SHEQEL":
        raise TestException("Bad country selector Value!")
    logger.info("Saving Preferences...")
    driver.find_element_by_css_selector('.glDefaultBtn').click()
    logger.info("Done Saving")
    # open_page(driver, 'http://anna.bglobale.de/online-store/dresses.html', 'offcanvas-overlay')
    logger.info("Searching for Clothing menu item...")
    wait_for_id(driver, 5, 'nav')
    nav_menu = driver.find_element_by_id('nav')
    spans = nav_menu.find_elements_by_tag_name('span')
    for span in spans:
        if "CLOTHING" in span.text:
            logger.info("Clothing entry found!")
            clothing_span = span
            break
    else:
        raise TestException("Test Failed! Clothing entry not found!")
    clothing_span.click()
    logger.info("Searching for Dresses in sidebar...")
    sidebar = driver.find_element_by_class_name('sidebar')
    spans = sidebar.find_elements_by_css_selector('li .level2 span')
    for span in spans:
        logger.debug("Span {0} {1}".format(span.tag_name, span.text))
        if "DRESSES" in span.text:
            logger.info("Dresses entry found!")
            dresses_span = span
            break
    else:
        raise TestException("Test Failed! Dresses entry not found!")
    dresses_span.click()
    wait_for_selector(driver, 5, '.item h2')
    logger.info("Searching for Crepe Jersey Fringe Cowl Dress...")
    products = driver.find_elements_by_css_selector('.item h2')
    for product in products:
        logger.info("{0} {1}".format(product.tag_name, product.text))
        if "Crepe Jersey Fringe Cowl Dress".upper() in product.text:
            logger.info("Product Found!")
            the_dress = product
            break
    else:
        raise TestException("Test Failed! Dresses entry not found!")
    the_dress.click()
    logger.info("Adding Product to bag...")
    wait_for_id(driver, 5, "attribute492")
    select = Select(driver.find_element_by_id("attribute492"))
    select.select_by_value('918')
    select.first_selected_option.click()
    driver.find_element_by_id("product-addtocart-button").click()
    logger.info("Product added to bag")
    logger.info("Checking Bag...")
    qty = driver.find_element_by_css_selector('.summary').text
    price = driver.find_element_by_css_selector('.price').text
    if qty != '1':
        raise TestException('Bad product QTY!')
    if u"₪" not in u"".join(price):
        raise TestException('Bad Prise Currency!')
    logger.info("Moving to Shopping bag...")
    driver.find_element_by_class_name("summary").click()
    wait_for_selector(driver, 10, ".checkout-types")
    # driver.find_element_by_css_selector(".checkout-types").click()
    logger.info("Moving to Checkout page")
    open_page(driver, 'http://anna.bglobale.de/onestepcheckout/', 'checkoutContainer')
    driver.switch_to.frame(driver.find_element_by_id("Intrnl_CO_Container"))
    token = driver.find_element_by_id('CheckoutData_CartToken')
    if token:
        logger.info("Token found: {0}".format(token.get_attribute('value')))
    else:
        raise TestException('Token not found!')
    logger.info("Filling user data...")
    driver.find_element_by_id('CheckoutData_BillingFirstName').send_keys('Samuel')
    driver.find_element_by_id('CheckoutData_BillingLastName').send_keys('Shapiro')
    driver.find_element_by_id('CheckoutData_Email').send_keys('test@test.com')
    select = Select(driver.find_element_by_id("BillingCountryID"))
    select.select_by_value('90')
    driver.find_element_by_id('CheckoutData_BillingAddress1').send_keys('M Hamoshavot')
    driver.find_element_by_id('BillingCity').send_keys('Petah Tikva')
    driver.find_element_by_id('BillingZIP').send_keys('0000000000')
    driver.find_element_by_id('CheckoutData_BillingPhone').send_keys('0000000000')
    # wait_for_selector(driver, 10, '.payMet-ccall')
    # driver.find_element_by_css_selector('.payMet-ccall').click()
    # driver.implicitly_wait(5)
    # driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element_by_id("secureWindow"))
    driver.find_element_by_id('cardNum').send_keys('4111111111111111')
    driver.find_element_by_id('cvdNumber').send_keys('111')
    select = Select(driver.find_element_by_id("cardExpiryYear"))
    select.select_by_value('2024')
    select = Select(driver.find_element_by_id("cardExpiryMonth"))
    select.select_by_value('7')
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element_by_id("Intrnl_CO_Container"))
    wait_for_id(driver, 10, 'btnPay')
    try:
        while True:
            wait_for_id(driver, 10, 'GE_Overlay')
    except (TimeoutException, TestException):
        logger.info("GE_OVerlay closed")
        pass
    driver.find_element_by_id('btnPay').click()
    # driver.switch_to.default_content()
    wait_for_id(driver, 30, 'orderConfirmationMessage')
    order_num = driver.find_element_by_class_name('orderRefNum')
    logger.info("Order {0} successfully received. Test completed".format(order_num.text))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(e)
        sys.exit(1)
