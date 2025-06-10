def create_chrome_driver(base_url: str) -> webdriver.Chrome:
    """Создание Chrome WebDriver с максимальной совместимостью для очень старых GPU"""
    chrome_options = Options()

    # ИСПРАВЛЕНО: Максимальная совместимость для GTX 550 Ti
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-gpu-sandbox")
    chrome_options.add_argument("--use-gl=disabled")
    chrome_options.add_argument("--enable-software-compositing")
    chrome_options.add_argument(
        "--disable-features=VizDisplayCompositor,AudioServiceOutOfProcess,TranslateUI,VizServiceDisplayCompositor"
    )
    chrome_options.add_argument("--timeout=120000")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")

    try:
        from webdriver_manager.chrome import ChromeDriverManager

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ИСПРАВЛЕНО: Увеличенные таймауты
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        print("✅ Chrome WebDriver оптимизирован для очень старой GPU (GTX 550 Ti)")
        return driver

    except Exception as e:
        print(f"❌ Ошибка Chrome WebDriver: {e}")
        pytest.skip(f"Chrome WebDriver недоступен: {e}")
