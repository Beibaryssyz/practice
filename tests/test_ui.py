import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.demoblaze.com'


def test_homepage_loads(driver):
    """TC-UI-01: Главная страница открывается корректно."""
    driver.get(BASE)
    time.sleep(1)
    assert 'STORE' in driver.title, f'Неверный заголовок: {driver.title}'
    logo = driver.find_element(By.CLASS_NAME, 'navbar-brand')
    assert logo.is_displayed(), 'Логотип не отображается'
    items = driver.find_elements(By.CLASS_NAME, 'card-title')
    assert len(items) > 0, 'Товары на главной странице не найдены'
    driver.save_screenshot('report/tc_ui_01.png')
    print(f'[OK] Заголовок: {driver.title}, товаров: {len(items)}')


def test_successful_login(driver):
    """TC-UI-02: Успешная авторизация пользователя."""
    driver.get(BASE)
    driver.find_element(By.ID, 'login2').click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, 'loginusername')))
    driver.find_element(By.ID, 'loginusername').send_keys('testuser200867')
    driver.find_element(By.ID, 'loginpassword').send_keys('Test1234!')
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()
    wait.until(EC.visibility_of_element_located((By.ID, 'logout2')))
    logout_btn = driver.find_element(By.ID, 'logout2')
    assert logout_btn.is_displayed(), 'Кнопка Log out не появилась после входа'
    driver.save_screenshot('report/tc_ui_02.png')


def test_login_wrong_password(driver):
    """TC-UI-03: Отказ при неверном пароле."""
    driver.get(BASE)
    driver.find_element(By.ID, 'login2').click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'loginusername')))
    driver.find_element(By.ID, 'loginusername').send_keys('testuser200867')
    driver.find_element(By.ID, 'loginpassword').send_keys('wrongpassword')
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        msg = alert.text
        alert.accept()
        driver.save_screenshot('report/tc_ui_03.png')
        print(f'[OK] Сообщение об ошибке получено: {msg}')
    except:
        driver.save_screenshot('report/tc_ui_03_fail.png')
        pytest.fail('Ожидался alert с сообщением об ошибке входа')


def test_add_to_cart(driver):
    """TC-UI-04: Добавление товара в корзину."""
    driver.get(BASE)
    first_item_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='card-block']//h4/a")))
    first_item_link.click()
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[text()='Add to cart']")))
    add_btn.click()
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    assert 'added' in alert.text.lower(), f'Неожиданный alert: {alert.text}'
    alert.accept()
    driver.save_screenshot('report/tc_ui_04.png')


def test_category_filter(driver):
    """TC-UI-05: Фильтрация каталога по категории 'Phones'."""
    driver.get(BASE)
    time.sleep(2)
    all_items = driver.find_elements(By.CLASS_NAME, 'card-title')
    count_before = len(all_items)
    phones_link = driver.find_element(By.LINK_TEXT, 'Phones')
    phones_link.click()
    time.sleep(2)
    filtered_items = driver.find_elements(By.CLASS_NAME, 'card-title')
    count_after = len(filtered_items)
    assert count_after > 0, 'После фильтрации не отображается ни одного товара'
    assert count_after <= count_before, 'Фильтр не уменьшил количество товаров'
    driver.save_screenshot('report/tc_ui_05.png')
    print(f'Было: {count_before}, стало после фильтра: {count_after}')
