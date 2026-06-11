import requests
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.demoblaze.com'

SQL_PAYLOADS = [
    ("' OR '1'='1",        "Классическая инъекция (всегда истина)"),
    ("' OR 1=1 --",         "Комментарий после условия"),
    ("admin'--",            "Обход пароля через комментарий"),
    ("' UNION SELECT 1--",  "UNION-инъекция"),
    ("'; DROP TABLE users--", "Попытка удаления таблицы"),
]

WEAK_PASSWORDS = [
    ('123',        'Слишком короткий (3 символа)'),
    ('password',   'Распространённый словарный пароль'),
    ('12345678',   'Только цифры'),
    ('aaaaaaaaa',  'Повторяющиеся символы'),
    ('user@test',  'Совпадает с именем пользователя'),
]

SECURITY_HEADERS = {
    'X-Frame-Options':          'Защита от clickjacking',
    'X-Content-Type-Options':   'Защита от MIME-sniffing',
    'Strict-Transport-Security': 'HSTS — принудительный HTTPS',
    'Content-Security-Policy':  'Защита от XSS',
    'X-XSS-Protection':         'Встроенная XSS-защита браузера',
    'Referrer-Policy':          'Контроль данных реферера',
}


def test_sql_injection_login(driver):
    """SEC-01: SQL-инъекции в форме входа."""
    driver.get(BASE)
    results = []
    for payload, desc in SQL_PAYLOADS:
        driver.find_element(By.ID, 'login2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'loginusername')))
        driver.find_element(By.ID, 'loginusername').clear()
        driver.find_element(By.ID, 'loginusername').send_keys(payload)
        driver.find_element(By.ID, 'loginpassword').clear()
        driver.find_element(By.ID, 'loginpassword').send_keys('anypassword')
        driver.find_element(By.XPATH, "//button[text()='Log in']").click()
        time.sleep(2)
        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept()
        except:
            pass
        logout_visible = len(driver.find_elements(By.ID, 'logout2')) > 0
        status = 'УЯЗВИМ' if logout_visible else 'ЗАЩИЩЁН'
        results.append((payload, desc, status))
        driver.save_screenshot(f'report/sec_01_{len(results)}.png')
        try:
            close_btn = driver.find_element(By.XPATH, "//div[@id='logInModal']//button[@class='close']")
            close_btn.click()
            time.sleep(0.5)
        except:
            pass
        driver.get(BASE)
        time.sleep(1)

    print('\n=== SEC-01: Результаты SQL-инъекций ===')
    for p, d, s in results:
        print(f'  {s:10s} │ {d:40s} │ {repr(p)}')
    assert all(r[2] == 'ЗАЩИЩЁН' for r in results), \
        'КРИТИЧНО: SQL-инъекция открыла доступ без пароля!'


def test_weak_password_registration(driver):
    """SEC-02: Регистрация со слабыми паролями."""
    driver.get(BASE)
    results = []
    for pwd, desc in WEAK_PASSWORDS:
        username = f'testuser_{int(time.time())}'
        driver.find_element(By.ID, 'signin2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'sign-username')))
        driver.find_element(By.ID, 'sign-username').clear()
        driver.find_element(By.ID, 'sign-username').send_keys(username)
        driver.find_element(By.ID, 'sign-password').clear()
        driver.find_element(By.ID, 'sign-password').send_keys(pwd)
        driver.find_element(By.XPATH, "//button[text()='Sign up']").click()
        time.sleep(1)
        try:
            alert = WebDriverWait(driver, 4).until(EC.alert_is_present())
            msg = alert.text
            alert.accept()
            accepted = 'successful' in msg.lower()
        except:
            accepted = False
        status = 'УЯЗВИМ (принят)' if accepted else 'OK (отклонён)'
        results.append((repr(pwd), desc, status))
        driver.save_screenshot(f'report/sec_02_{len(results)}.png')
    print('\n=== SEC-02: Политика паролей ===')
    for pw, d, s in results:
        print(f'  {s:20s} │ {d}')


def test_security_headers():
    """SEC-03: Проверка защитных HTTP-заголовков."""
    assert BASE.startswith('https://'), 'Сайт работает по HTTP!'
    r = requests.get(BASE, timeout=10)
    print('\n=== SEC-03: Заголовки безопасности ===')
    missing = []
    for header, desc in SECURITY_HEADERS.items():
        val = r.headers.get(header, None)
        status = f'[OK] {val}' if val else '[ОТСУТСТВУЕТ]'
        print(f'  {header:35s}: {status}')
        print(f'    ({desc})')
        if not val:
            missing.append(header)
    print(f'\nИтого: отсутствует {len(missing)} из {len(SECURITY_HEADERS)} заголовков')
    if missing:
        print(f'Отсутствующие: {missing}')
    critical = [h for h in missing if h in ['X-Frame-Options', 'X-Content-Type-Options']]
    assert not critical, f'Критичные защитные заголовки отсутствуют: {critical}'
