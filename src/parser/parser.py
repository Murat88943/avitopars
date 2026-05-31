import json, time, random, re, os
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

config_path = '/home/murat/avito-monitor/src/config/config.json'
with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
settings = config['settings']
CACHE_DIR = '/home/murat/avito-monitor/cache'
os.makedirs(CACHE_DIR, exist_ok=True)

CITY_MAP = {
    'москва': 'moskva', 'москве': 'moskva', 'мск': 'moskva',
    'санкт-петербург': 'sankt-peterburg', 'спб': 'sankt-peterburg', 'питер': 'sankt-peterburg', 'ленинград': 'sankt-peterburg',
    'подольск': 'podolsk', 'люберцы': 'lyubertsy', 'мытищи': 'mytishchi', 'королев': 'korolev', 'балашиха': 'balashiha',
    'химки': 'himki', 'красногорск': 'krasnogorsk', 'одинцово': 'odintsovo', 'домодедово': 'domodedovo', 'чехов': 'chekhov',
    'серпухов': 'serpukhov', 'коломна': 'kolomna', 'электросталь': 'elektrostal', 'орехово-зуево': 'orehovo-zuevo',
    'сергиев посад': 'sergiev_posad', 'наро-фоминск': 'naro-fominsk', 'воскресенск': 'voskresensk', 'шатура': 'shatura',
    'дмитров': 'dmitrov', 'егорьевск': 'egorevsk', 'всеволожск': 'vsevolozhsk', 'гатчина': 'gatchina', 'выборг': 'vyborg',
    'сосновый бор': 'sosnovy_bor', 'тихвин': 'tihvin', 'кириши': 'kirishi', 'кингисепп': 'kingisepp', 'волхов': 'volhov',
    'лодейное поле': 'lodeynoe_pole', 'приозерск': 'priozersk', 'тверь': 'tver', 'рязань': 'ryazan', 'ярославль': 'yaroslavl',
    'кострома': 'kostroma', 'иваново': 'ivanovo', 'владимир': 'vladimir', 'калуга': 'kaluga', 'тула': 'tula', 'орел': 'orel',
    'брянск': 'bryansk', 'курск': 'kursk', 'белгород': 'belgorod', 'липецк': 'lipetsk', 'тамбов': 'tambov', 'воронеж': 'voronezh',
    'смоленск': 'smolensk', 'вологда': 'vologda', 'череповец': 'cherepovets', 'великий новгород': 'velikiy_novgorod', 'псков': 'pskov',
    'нижний новгород': 'nizhniy-novgorod', 'н.новгород': 'nizhniy-novgorod', 'казань': 'kazan', 'самара': 'samara', 'уфа': 'ufa',
    'пермь': 'perm', 'екатеринбург': 'ekaterinburg', 'чебоксары': 'cheboksary', 'саранск': 'saransk', 'ижевск': 'izhevsk',
    'киров': 'kirov', 'ульяновск': 'ulyanovsk', 'тольятти': 'tolyatti', 'набережные челны': 'naberezhnye_chelny', 'пенза': 'penza',
    'саратов': 'saratov', 'волгоград': 'volgograd', 'астрахань': 'astrahan', 'йошкар-ола': 'yoshkar-ola', 'оренбург': 'orenburg',
    'тюмень': 'tyumen', 'челябинск': 'chelyabinsk', 'магнитогорск': 'magnitogorsk', 'курган': 'kurgan', 'сургут': 'surgut',
    'нижневартовск': 'nzhnevartovsk', 'нефтеюганск': 'nefteyugansk', 'новый уренгой': 'novy_urengoy', 'ноябрьск': 'noyabrsk',
    'хмао': 'hanty-mansiysk', 'ханты-мансийск': 'hanty-mansiysk', 'салехард': 'salekhard', 'янао': 'salekhard',
    'новосибирск': 'novosibirsk', 'омск': 'omsk', 'томск': 'tomsk', 'кемерово': 'kemerovo', 'новокузнецк': 'novokuznetsk',
    'прокопьевск': 'prokopevsk', 'ленинск-кузнецкий': 'leninsk-kuznetskiy', 'красноярск': 'krasnoyarsk', 'норильск': 'norilsk',
    'ачинск': 'achinsk', 'канск': 'kansk', 'иркутск': 'irkutsk', 'ангарск': 'angarsk', 'братск': 'bratsk', 'усть-илимск': 'ust-ilimsk',
    'чита': 'chita', 'улан-удэ': 'ulan-ude', 'барнаул': 'barnaul', 'бийск': 'biysk', 'рубцовск': 'rubtsovsk', 'горно-алтайск': 'gorno-altaysk',
    'кызыл': 'kyzyl', 'абакан': 'abakan', 'владивосток': 'vladivostok', 'хабаровск': 'habarovsk', 'комсомольск-на-амуре': 'komsomolsk-na-amure',
    'благовещенск': 'blagoveshchensk', 'белогорск': 'belogorsk', 'южно-сахалинск': 'yuzhno-sahalinsk', 'корсаков': 'korsakov',
    'петропавловск-камчатский': 'petropavlovsk-kamchatskiy', 'магадан': 'magadan', 'якутск': 'yakutsk', 'нерюнгри': 'neryungri',
    'уссурийск': 'ussuriysk', 'артем': 'artem', 'нахотка': 'nahodka', 'бикин': 'bikin', 'амурск': 'amursk', 'свободный': 'svobodny',
    'райчихинск': 'raychihinsk', 'махачкала': 'mahachkala', 'хасавюрт': 'hasavyurt', 'дербент': 'derbent', 'каспийск': 'kaspiysk',
    'грозный': 'grozny', 'аргун': 'ar gun', 'назрань': 'nazran', 'владикавказ': 'vladikavkaz', 'беслан': 'beslan', 'нальчик': 'nalchik',
    'черкесск': 'cherkessk', 'ставрополь': 'stavropol', 'пятигорск': 'pyatigorsk', 'кисловодск': 'kislovodsk', 'ессентуки': 'essentuki',
    'минеральные воды': 'mineralnye_vody', 'невинномысск': 'nevinnomyssk', 'буденновск': 'budennovsk', 'ростов-на-дону': 'rostov-na-donu',
    'ростов': 'rostov-na-donu', 'таганрог': 'taganrog', 'шахты': 'shakhty', 'волгодонск': 'volgodonsk', 'новочеркасск': 'novocherkassk',
    'батайск': 'bataysk', 'краснодар': 'krasnodar', 'сочи': 'sochi', 'новороссийск': 'novorossiysk', 'армавир': 'armavir', 'анапа': 'anapa',
    'геленджик': 'gelendzhik', 'крымск': 'krymsk', 'белореченск': 'belorechensk', 'тихорецк': 'tihoretsk', 'ейск': 'eysk', 'лабинск': 'labinsk',
    'кропоткин': 'kropotkin', 'славянск-на-кубани': 'slavyansk-na-kubani', 'туапсе': 'tuapse', 'севастополь': 'sevastopol',
    'симферополь': 'simferopol', 'керчь': 'kerch', 'ялта': 'yalta', 'евпатория': 'evpatoriya', 'феодосия': 'feodosiya', 'донецк': 'donetsk_ros',
    'каменск-шахтинский': 'kamensk-shahtinskiy', 'архангельск': 'arhangelsk', 'северодвинск': 'severodvinsk', 'котлас': 'kotlas',
    'мурманск': 'murmansk', 'апатиты': 'apatity', 'североморск': 'severomorsk', 'кандалакша': 'kandalaksha', 'мончегорск': 'monchegorsk',
    'петрозаводск': 'petrozavodsk', 'кондопога': 'kondopoga', 'сегежа': 'segezha', 'сыктывкар': 'syktyvkar', 'ухта': 'uhta',
    'воркута': 'vorkuta', 'печора': 'pechora', 'инта': 'inta', 'калининград': 'kaliningrad', 'советск': 'sovetsk', 'черняховск': 'chernyahovsk',
    'орск': 'orsk', 'новотроицк': 'novotroitsk', 'бузулук': 'buzuluk', 'альметьевск': 'almetevsk', 'зеленодольск': 'zelenodolsk',
    'бугульма': 'bugulma', 'елабуга': 'elabuga', 'нижнекамск': 'nizhnekamsk', 'каменск-уральский': 'kamensk-uralskiy', 'первоуральск': 'pervouralsk',
    'серов': 'serov', 'новоуральск': 'novouralsk', 'бердск': 'berdsk', 'искитим': 'iskitim', 'куйбышев': 'kuybyshev', 'судак': 'sudak',
    'алушта': 'alushta', 'бахчисарай': 'bahchisaray', 'саки': 'saki', 'армянск': 'armyansk', 'красноперекопск': 'krasnoperekopsk',
    'железногорск': 'zheleznogorsk', 'зеленогорск': 'zelenogorsk', 'северск': 'seversk', 'саров': 'sarov', 'мирный': 'mirny',
    'знаменск': 'znamensk', 'радужный': 'raduzhny', 'майкоп': 'maykop', 'элиста': 'elista'
}

CATEGORY_MAP = {}
if 'parsing' in config and 'categories' in config['parsing']:
    CATEGORY_MAP = {v.lower(): k for k, v in config['parsing']['categories'].items()}
    for eng, rus in config['parsing']['categories'].items():
        CATEGORY_MAP[rus.lower()] = eng; CATEGORY_MAP[eng] = eng

def clean_avito_url(url):
    if not url: return url
    try:
        parsed = urlparse(url)
        query_params = {}
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param: key, value = param.split('=', 1); query_params[key] = value
        for param in ['context', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'from', 'via']:
            if param in query_params: del query_params[param]
        new_query = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        cleaned_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
        return cleaned_url[:-1] if cleaned_url.endswith('?') else cleaned_url
    except Exception: return url

def normalize_city(city_input):
    if not city_input or city_input.strip() == '': return None
    city_input = city_input.lower().strip()
    if city_input in ['все', 'все города', 'россия', 'russia', 'all', '*']: return None
    if city_input in CITY_MAP: return CITY_MAP[city_input]
    for key, value in CITY_MAP.items():
        if key in city_input or city_input in key: return value
    normalized = city_input.replace(' ', '-')
    return normalized if normalized in CITY_MAP.values() else normalized

def normalize_category(category_input):
    category_input = category_input.lower().strip()
    if category_input in CATEGORY_MAP: return CATEGORY_MAP[category_input]
    for key, value in CATEGORY_MAP.items():
        if key in category_input or category_input in key: return value
    return None

def load_cached_page(url):
    cache_file = os.path.join(CACHE_DIR, f"{hash(url)}.html")
    if os.path.exists(cache_file) and datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file)) < timedelta(minutes=30):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f: return f.read()
        except: pass
    return None

def save_to_cache(url, content):
    try:
        with open(os.path.join(CACHE_DIR, f"{hash(url)}.html"), 'w', encoding='utf-8') as f: f.write(content)
    except: pass

def human_delay(): time.sleep(random.uniform(2, 5))

def random_scroll(page):
    for _ in range(random.randint(2, 5)):
        page.evaluate(f'window.scrollBy(0, {random.randint(300, 800)})'); time.sleep(random.uniform(0.5, 1.2))

def wait_for_page_load(page, timeout=30):
    try: page.wait_for_load_state('networkidle', timeout=timeout*1000); print("  📡 Сеть стабилизировалась")
    except: print("  ⚠️ Таймаут ожидания сети, продолжаем...")
    try: page.wait_for_load_state('domcontentloaded', timeout=timeout*1000); print("  📄 DOM загружен")
    except: print("  ⚠️ Таймаут ожидания DOM")
    additional_delay = random.uniform(3, 6); print(f"  ⏳ Ожидание полной отрисовки страницы ({additional_delay:.1f} сек)..."); time.sleep(additional_delay)

def extract_items_from_page(page):
    items = []; time.sleep(random.uniform(1, 2))
    try: page.wait_for_selector('div[data-marker="item"]', timeout=15000); print("  🎯 Селектор объявлений найден")
    except: print("  ⚠️ Селектор объявлений не найден, пробуем другие методы")
    human_delay(); random_scroll(page); time.sleep(random.uniform(1.5, 3)); print("  🔄 Ждем подгрузки динамического контента...")
    item_elements = page.query_selector_all('div[data-marker="item"]')
    if not item_elements: item_elements = page.query_selector_all('[class*="item"]')
    print(f"  Найдено элементов: {len(item_elements)}")
    for item in item_elements:
        try:
            title = None
            for selector in ['h3', '[itemprop="name"]', 'a[data-marker="item-title"]', 'h3[class*="title"]']:
                title_elem = item.query_selector(selector)
                if title_elem: title = title_elem.inner_text().strip()
                if title and len(title) > 2: break
            if not title or len(title) < 3:
                link_elem = item.query_selector('a')
                if link_elem: title = link_elem.inner_text().strip()
                if title: title = re.sub(r'\s+', ' ', title)
                else: title = None
            if not title: continue
            price = "Цена не указана"
            for selector in ['[itemprop="price"]', 'span[data-marker*="price"]', 'span[class*="price"]', 'meta[itemprop="price"]']:
                price_elem = item.query_selector(selector)
                if price_elem:
                    price = price_elem.get_attribute('content') if price_elem.get_attribute('content') else price_elem.inner_text().strip()
                    if price: break
            link = ""
            for selector in ['a[data-marker="item-title"]', 'a[href*="/moskva/"]', 'a[href*="_"]']:
                link_elem = item.query_selector(selector)
                if link_elem:
                    link = link_elem.get_attribute('href')
                    if link:
                        if not link.startswith('http'): link = 'https://www.avito.ru' + link
                        link = clean_avito_url(link); break
            items.append({'title': title, 'price': price, 'link': link})
        except Exception: continue
    return items

def save_results_to_files(results, city, query, pages=1, category=None):
    output_dir = settings.get('output_path', '/home/murat/avito-monitor/results')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_for_filename = city if city else "rossiya"
    filename_parts = [city_for_filename.replace(' ', '_'), query.replace(' ', '_')]
    if category: filename_parts.insert(1, category.replace(' ', '_'))
    base_filename = f"{'_'.join(filename_parts)}_{timestamp}"
    simple_output_file = os.path.join(output_dir, f"{base_filename}_items.json")
    with open(simple_output_file, 'w', encoding='utf-8') as f: json.dump(results, f, ensure_ascii=False, indent=2)
    full_output_file = os.path.join(output_dir, f"{base_filename}_full.json")
    metadata = {"parse_info": {"city": city if city else "Вся Россия", "city_slug": city if city else "all", "query": query,
                "category": category if category else "all", "pages": pages, "total_items": len(results),
                "timestamp": datetime.now().isoformat(), "date": datetime.now().strftime("%Y-%m-%d"), "time": datetime.now().strftime("%H:%M:%S")}, "items": results}
    with open(full_output_file, 'w', encoding='utf-8') as f: json.dump(metadata, f, ensure_ascii=False, indent=2)
    return simple_output_file, full_output_file

def print_pretty_results(results, city, query, category=None):
    print("\n" + "=" * 80); print(f"📊 РЕЗУЛЬТАТЫ ПАРСИНГА"); print("=" * 80)
    if city: print(f"🏙️  Город: {city}")
    else: print(f"🇷🇺  Регион: ВСЯ РОССИЯ")
    print(f"🔍 Поисковый запрос: {query}")
    if category: print(f"📂 Категория: {category}")
    print(f"📊 Всего найдено: {len(results)} объявлений")
    print(f"🕐 Время парсинга: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"); print("=" * 80)
    if results:
        print(f"\n📋 Детальный список объявлений:"); print("-" * 80)
        for i, item in enumerate(results, 1):
            print(f"\n{i}. 📱 {item['title']}"); print(f"   💰 Цена: {item['price']} ₽")
            short_link = item['link'][:80] + "..." if len(item['link']) > 80 else item['link']; print(f"   🔗 Ссылка: {short_link}"); print("-" * 80)
        prices = []
        for item in results:
            price_str = item['price'].replace(' ', '').replace('₽', '').strip()
            if price_str and price_str != 'Цена не указана':
                try:
                    price_num = re.search(r'(\d+)', price_str)
                    if price_num: prices.append(int(price_num.group(1)))
                except: pass
        if prices:
            print(f"\n📊 Статистика по ценам:")
            print(f"   • Минимальная цена: {min(prices):,} ₽".replace(',', ' '))
            print(f"   • Средняя цена: {sum(prices) // len(prices):,} ₽".replace(',', ' '))
            print(f"   • Максимальная цена: {max(prices):,} ₽".replace(',', ' '))
    else: print("\n❌ Объявления не найдены.\nВозможные причины:\n  • Нет объявлений по вашему запросу\n  • Проблемы с загрузкой страницы\n  • Блокировка со стороны Avito")

def parse_avito_playwright(city, query, category=None, pages=1):
    all_items = []; city_slug = normalize_city(city)
    if city_slug is None: print("🌍 Поиск по ВСЕЙ РОССИИ (без ограничения по городу)"); base_url_template = "https://www.avito.ru"
    else: print(f"🏙️ Город в URL: {city_slug}"); base_url_template = f"https://www.avito.ru/{city_slug}"
    with sync_playwright() as p:
        user_agent = config['headers']['User-Agent']
        if settings.get('use_random_user_agent', False) and 'user_agents' in config: user_agent = random.choice(config['user_agents'])
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled', '--no-sandbox',
            '--disable-dev-shm-usage', '--disable-web-security', '--disable-features=IsolateOrigins,site-per-process'])
        context = browser.new_context(user_agent=user_agent, viewport={'width': random.choice([1366, 1440, 1920]), 'height': 1080},
            locale='ru-RU', extra_http_headers={'Accept-Language': 'ru-RU,ru;q=0.9'})
        context.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]}); window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru']});""")
        page = context.new_page(); print("🌐 Устанавливаю сессию..."); page.goto('https://www.avito.ru/', timeout=60000)
        wait_for_page_load(page, timeout=20); human_delay()
        for page_num in range(1, pages + 1):
            category_slug = normalize_category(category) if category else None
            if category_slug:
                url = f"{base_url_template}/{category_slug}?q={query}&p={page_num}" if category_slug else f"{base_url_template}?q={query}&p={page_num}"
            else: url = f"{base_url_template}?q={query}&p={page_num}"
            print(f"\n📄 Страница {page_num}: {url}")
            retry_count, max_retries = 0, 3
            while retry_count < max_retries:
                try:
                    cached_html = load_cached_page(url)
                    if cached_html:
                        print("  📦 Загружено из кэша"); page.set_content(cached_html); wait_for_page_load(page, timeout=15)
                    else:
                        print("  🌐 Загружаем страницу..."); page.goto(url, timeout=60000, wait_until='domcontentloaded')
                        wait_for_page_load(page, timeout=25); dynamic_delay = random.uniform(2, 4)
                        print(f"  🔄 Дополнительная задержка для динамики ({dynamic_delay:.1f} сек)..."); time.sleep(dynamic_delay); save_to_cache(url, page.content())
                    if page.query_selector('text=/Доступ ограничен|проблема с IP|капча|captcha/i'):
                        print(f"  ⚠️ Страница {page_num} заблокирована, попытка {retry_count + 1}/{max_retries}")
                        retry_count += 1; time.sleep(30 * retry_count); continue
                    time.sleep(random.uniform(1, 2)); items = extract_items_from_page(page)
                    if items:
                        print(f"  ✅ Найдено объявлений: {len(items)}"); all_items.extend(items); break
                    else:
                        print(f"  ⚠️ Не найдено объявлений"); html = page.content()
                        with open(f'debug_page_{page_num}_{int(time.time())}.html', 'w', encoding='utf-8') as f: f.write(html)
                        print(f"  📁 HTML сохранен для отладки"); break
                except Exception as e:
                    print(f"  ❌ Ошибка: {e}, попытка {retry_count + 1}/{max_retries}"); retry_count += 1
                    if retry_count < max_retries: time.sleep(15 * retry_count)
                    else: break
            if page_num < pages: delay = settings['delay_between_requests'] + random.uniform(8, 15); print(f"  ⏱️ Пауза между страницами {delay:.1f} сек..."); time.sleep(delay)
        browser.close()
    return all_items

def show_categories():
    if 'parsing' in config and 'categories' in config['parsing']:
        print("\n📂 Доступные категории:"); print("-" * 40)
        for eng, rus in config['parsing']['categories'].items(): print(f"  • {rus} ({eng})")
        print()

def show_city_help():
    print("\n🏙️  Введите город (на русском):"); print("   • Москва, Санкт-Петербург, Казань, Екатеринбург")
    print("   • Владивосток, Сочи, Краснодар, Нижний Новгород"); print("   • И более 500 других городов РФ")
    print("\n💡 Для поиска по ВСЕЙ РОССИИ просто нажмите Enter")

if __name__ == "__main__":
    print("=" * 50); print("🚀 Avito Parser (Расширенная версия)"); print("=" * 50); show_city_help()
    city = input("\nГород (Enter для поиска по всей России): ").strip()
    if not city: city = None; print("  🌍 Выполняется поиск по ВСЕЙ РОССИИ")
    else: print(f"  🏙️ Выбран город: {city}")
    show_categories(); print("💡 Для поиска по всем категориям просто нажмите Enter")
    category = input("Категория (необязательно): ").strip()
    if not category: category = None; print("  Поиск по всем категориям")
    query = input("\n🔍 Введите товар: ").strip()
    if not query: query = input("❌ Товар не указан. Введите товар: ").strip()
    pages_input = input("📑 Сколько страниц (по умолчанию 1): ").strip()
    pages = int(pages_input) if pages_input.isdigit() else 1
    print(f"\n🚀 Начинаю парсинг:")
    if city: print(f"   Город: {city}")
    else: print(f"   Регион: ВСЯ РОССИЯ")
    print(f"   Категория: {category if category else 'Все категории'}"); print(f"   Товар: {query}"); print(f"   Страниц: {pages}"); print("=" * 50)
    results = parse_avito_playwright(city, query, category, pages)
    print_pretty_results(results, city, query, category)
    if results:
        simple_file, full_file = save_results_to_files(results, city, query, pages, category)
        print(f"\n💾 Результаты сохранены:"); print(f"   • Только объявления: {simple_file}"); print(f"   • С метаданными: {full_file}")
        default_file = f'results_{query.replace(" ", "_")}.json'
        with open(default_file, 'w', encoding='utf-8') as f: json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"   • Стандартный файл: {default_file}")
    else: print("\n❌ Объявления не найдены. Результаты не сохранены.")