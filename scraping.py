"""
detailページへはボタンで遷移する
"""

import time
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


def remove_non_number(text):
    divided_number = re.findall(r'\d+', text)  # 文字列から数字にマッチするものをリストとして取得
    integrate_only_number = ''.join(divided_number)
    integrate_only_number = re.sub(r'\D', '', text)  # 元の文字列から数字以外を削除＝数字を抽出
    return divided_number , integrate_only_number




def html_table_tag_to_csv_list(table_tag_str: str, header_exist: bool = True):
    table_soup = BeautifulSoup(table_tag_str, 'html.parser')
    rows = []
    if header_exist:
        for tr in table_soup.find_all('tr'):
            cols = [] 
            for td in tr.find_all(['td', 'th']):
                cols.append(td.text.strip())
            rows.append(cols)
    else:
        for tbody in table_soup.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                cols = [td.text.strip() for td in tr.find_all(['td', 'th'])]
                rows.append(cols)
    return rows



class Reins_Scraper:
    def __init__(self, browse_visually = "no"):
        self.driver = self.browser_setup(browse_visually)
        self.wait_driver = WebDriverWait(self.driver, 5)

    def browser_setup(self , browse_visually = "no"):
        """ブラウザを起動する関数"""
        #ブラウザの設定
        options = webdriver.ChromeOptions()
        if browse_visually == "no":
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        #ブラウザの起動
        browser = webdriver.Chrome(options=options , service=ChromeService(ChromeDriverManager().install()))
        browser.implicitly_wait(3)
        return browser
    
    def login_reins(self, login_url: str , user_id: str , password: str ,):
        self.driver.get(login_url)
        time.sleep(2)

        login_flag = "No"
        # ログインボタンをクリック
        try:
            login_button = self.wait_driver.until(EC.element_to_be_clickable((By.ID, "login-button")))
            login_button.click()
        except:
            maintenance = self.wait_driver.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.p-card"))).text
            return maintenance

        # フォームにログイン認証情報を入力
        user_id_form = self.wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        user_id_form.send_keys(user_id)
        password_form = self.wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_form.send_keys(password)
        rule_element = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and contains(following-sibling::label, 'ガイドライン')]")))
        rule_checkbox_form = rule_element.find_element(By.XPATH, "./following-sibling::label")
        rule_checkbox_form.click()
        time.sleep(0.5)
        login_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'ログイン')]")))
        login_button.click()
        login_flag = "OK"
        return login_flag

    def get_solding_or_rental_option(self):
        # ボタン「売買 物件検索」をクリック
        sold_building_search_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '売買') and contains(text(), '物件検索')]")))
        sold_building_search_button.click()
        time.sleep(1)
        # 検索条件を取得
        display_search_method_link = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='card p-card'])[1]"))).find_element(By.XPATH, ".//a[contains(span, '検索条件を表示')]")
        display_search_method_link.click()
        time.sleep(1)
        # 検索条件のリストを取得
        select_element = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//div[@class='p-selectbox']//select")))
        search_method_element_list = select_element.find_elements(By.TAG_NAME, "option")
        solding_search_method_list = []
        for search_method_element in search_method_element_list:
            solding_search_method_list.append( search_method_element.text )
        # 前のページに戻る
        self.driver.back()

        # ボタン「売買 物件検索」をクリック
        rental_building_search_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '賃貸') and contains(text(), '物件検索')]")))
        rental_building_search_button.click()
        time.sleep(1)
        # 検索条件を取得
        display_search_method_link = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='card p-card'])[1]"))).find_element(By.XPATH, ".//a[contains(span, '検索条件を表示')]")
        display_search_method_link.click()
        time.sleep(1)
        # 検索条件のリストを取得
        select_element = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//div[@class='p-selectbox']//select")))
        search_method_element_list = select_element.find_elements(By.TAG_NAME, "option")
        rental_search_method_list = []
        for search_method_element in search_method_element_list:
            rental_search_method_list.append( search_method_element.text )
        # 前のページに戻る
        self.driver.back()
        time.sleep(2)
        return solding_search_method_list , rental_search_method_list
        
    def scraping_solding_list(self , searched_url: str , search_method_value: str , index_of_search_requirement: int):
        self.driver.get(searched_url)
        time.sleep(1)

        # 選択された検索方法をクリック
        if search_method_value == "search_solding":
            building_search_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '売買') and contains(text(), '物件検索')]")))
            building_search_button.click()
            time.sleep(1)
        else:
            building_search_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '賃貸') and contains(text(), '物件検索')]")))
            building_search_button.click()
            time.sleep(1)

        # 売買検索条件を選択
        display_search_method_link = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='card p-card'])[1]"))).find_element(By.XPATH, ".//a[contains(span, '検索条件を表示')]")
        display_search_method_link.click()
        time.sleep(1)
        choice_search_method = Select(self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//div[@class='p-selectbox']//select"))))
        choice_search_method.select_by_index(index_of_search_requirement)
        get_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '読込')]")))
        get_button.click()
        time.sleep(1)
        time.sleep(0.5)

        # 検索条件が存在するか判定
        exist_search_requirement_sentence = self.wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="modal"]'))).text
        if "エラー" in exist_search_requirement_sentence:
            to_csv_list = False
            return to_csv_list
        
        ok_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'OK')]")))
        ok_button.click()
        time.sleep(1)

        # 検索条件に基づいて検索実行
        search_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//div[@class='p-frame-bottom']//button[contains(text(), '検索')]")))
        search_button.click()
        time.sleep(2)

        # 物件リストが何ページあるかを判定
        time.sleep(2)
        page_count_info = self.wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-header"))).text
        match = re.search(r'(\d+)件', page_count_info)
        total_number = int( match.group(1) )
        left_page_count = total_number / 50 

        # リストを取得
        loop_count = 0
        all_list = []
        while True:
            # 印刷表示ボタンをクリック
            print_button = self.wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '印刷')]")))
            print_button.click()
            time.sleep(2)
            
            # 現在のページのHTML要素を取得
            table_tag_str = self.wait_driver.until(EC.presence_of_element_located((By.TAG_NAME, "table"))).get_attribute('outerHTML')
            # tableタグの要素を多次元リストに変換
            if loop_count == 0:
                header_exist = True
            else:
                header_exist = False
            loop_count += 1

            to_csv_list = html_table_tag_to_csv_list(
                table_tag_str = table_tag_str , header_exist = header_exist ,
            )
            all_list.append(to_csv_list)

            if left_page_count >= 1:
                left_page_count -= 1
                # リストの表示ページへ戻る
                back_button = self.wait_driver.until(EC.element_to_be_clickable((By.CLASS_NAME, 'p-frame-backer')))
                back_button.click()
                time.sleep(2)
                # 次のリストを表示させるボタンをクリック
                next_list_button = self.wait_driver.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.page-item > button > span.p-pagination-next-icon')))
                next_list_button.click()
                time.sleep(2)

            else:
                break
        
        # 全ての多次元リストを連結
        to_csv_list = []
        for loop in range( len(all_list) ):
            to_csv_list.extend( all_list[loop] )    
        
        return to_csv_list
    




def main():
    page_url = "https://www.google.com/"

if __name__ == "__main__":
    main()
