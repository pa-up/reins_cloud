"""
定期実行において、「売買物件検索の中で名前に「土地」という文字が
入っているもの」だけ を抽出するといった仕様

日時指定のための各種設定を本WEBアプリで編集
    日時指定のスクレイピング実行はLambda・S3とRender上
"""

from flask import Flask, render_template, request , send_file , redirect , url_for , session
import os
import time
import re

import excel_or_csv as ec
from scraping import Reins_Scraper
import py_mail
from aws import ManipulateS3


# flaskアプリの明示
templates_path = "templates/"
static_path = "static/"
app = Flask(__name__ , template_folder=templates_path, static_folder=static_path)

# パスの定義
mail_excel_path = static_path + "input_excel/email_pw.xlsx"
search_method_csv_path = static_path + "csv/search_method.csv"
search_method_excel_path = static_path + "input_excel/search_method.xlsx"
output_reins_csv_path_from_static = "csv/output_reins.csv"
output_reins_csv_path = static_path + output_reins_csv_path_from_static
output_reins_excel_path = static_path + "output_excel/output_reins.xlsx"


# 環境変数の取得
user_id , password = os.environ.get('SECRET_USER_ID') , os.environ.get('SECRET_PASSWORD')
s3_accesskey , s3_secretkey = os.environ.get('S3_ACCESSKEY') , os.environ.get('S3_SECRETKEY')
s3_bucket_name = os.environ.get('S3_BUCKET_NAME')

# s3の定義
s3_region = "ap-northeast-1"   # 東京(アジアパシフィック)：ap-northeast-1
manipulate_s3 = ManipulateS3(
    region = s3_region ,
    accesskey = s3_accesskey ,
    secretkey = s3_secretkey ,
    bucket_name = s3_bucket_name ,
)


# S3からメール情報や検索条件を取得し、静的フォルダに格納
manipulate_s3 = ManipulateS3(
    region = "ap-northeast-1" ,
    accesskey = s3_accesskey ,
    secretkey = s3_secretkey ,
    bucket_name = s3_bucket_name ,
)



@app.route('/')
def index():
        return render_template("index.html")


@app.route('/order_scraping')
def order_scraping():
    global reins_sraper , solding_search_method_list , rental_search_method_list

    # ページにアクセス
    login_url = "https://system.reins.jp/"
    reins_sraper = Reins_Scraper()

    # ログイン突破
    login_flag = reins_sraper.login_reins(login_url , user_id , password)
    if login_flag == "OK":
        solding_search_method_list , rental_search_method_list = reins_sraper.get_solding_or_rental_option()
        print(f"solding_search_method_list : {solding_search_method_list} \n")
        print(f"rental_search_method_list : {rental_search_method_list} \n")

        return render_template(
            "order_scraping.html" ,
            solding_search_method_list = solding_search_method_list ,
            rental_search_method_list = rental_search_method_list ,
            login_flag = login_flag ,
        )
    else:
        return render_template(
            "order_scraping.html" ,
            login_flag = login_flag ,
        )


@app.route('/result', methods=['GET', 'POST'])
def result():
    global reins_sraper , solding_search_method_list , rental_search_method_list
    if request.method == 'POST' and request.form['start_scraping'] == "true":
        # フォームから検索方法を取得
        search_method_value = request.form['search_method_value']
        # フォームから検索条件を取得
        search_requirement = request.form['solding'] if search_method_value == 'search_solding' else request.form['rental']
        print(f"search_requirement : {search_requirement} \n")

        if search_method_value == "search_solding":
            index_of_search_requirement = solding_search_method_list.index(search_requirement)
            print(f"index_of_search_requirement : {index_of_search_requirement} \n")
        else:
            index_of_search_requirement = rental_search_method_list.index(search_requirement)
            print(f"index_of_search_requirement : {index_of_search_requirement} \n")

        
        # リストの取得実行
        searched_url = "https://system.reins.jp/main/KG/GKG003100"
        to_csv_list = reins_sraper.scraping_solding_list(searched_url , search_method_value , index_of_search_requirement)
        reins_sraper.driver.quit()
        if to_csv_list == False:
            return render_template(
                "result.html" ,
                search_method_value = search_method_value ,
                search_requirement = search_requirement ,
                no_exist_search_requirement = True ,
            )
        
        # リストをCSVファイルに保存
        ec.list_to_csv(to_csv_list = to_csv_list , csv_path = output_reins_csv_path ,)
        # リストをExcelファイルに保存
        ec.list_to_excel(to_csv_list , output_reins_excel_path)

        return render_template(
            "result.html" ,
            search_method_value = search_method_value ,
            search_requirement = search_requirement ,
            csv_path_from_static = output_reins_csv_path_from_static ,
        )
    

@app.route('/schedule_search')
def schedule_search():
    global reins_sraper , solding_search_method_list , rental_search_method_list

    # ページにアクセス
    login_url = "https://system.reins.jp/"
    reins_sraper = Reins_Scraper()

    # ログイン突破
    login_flag = reins_sraper.login_reins(login_url , user_id , password)
    if login_flag == "OK":
        # 現時点での全ての検索条件の選択肢を表示
        solding_search_method_list , rental_search_method_list = reins_sraper.get_solding_or_rental_option()
        
        print(f"solding_search_method_list : {solding_search_method_list} \n")
        print(f"rental_search_method_list : {rental_search_method_list} \n")

        # 検索条件をcsvファイルをS3から取得
        manipulate_s3.s3_file_download(search_method_excel_path)
        time.sleep(2)

        # 日時実行の検索条件をExcelファイルから取得
        """ クラウドの定期実行ファイルでも同様に取得 """
        index_of_solding_requirement_list, index_of_rental_requirement_list = ec.get_search_option_from_excel(search_method_excel_path)
        index_of_solding_requirement_list = [x for x in index_of_solding_requirement_list if x not in (0, None)]
        index_of_rental_requirement_list = [x for x in index_of_rental_requirement_list if x not in (0, None)]

        print()
        print(f"===========")
        print(index_of_solding_requirement_list)
        print(index_of_rental_requirement_list)

        past_select_solding_list = []
        past_select_rental_list = []
        for loop , index_of_solding_requirement in enumerate(index_of_solding_requirement_list):
            past_select_solding_list.append(solding_search_method_list[index_of_solding_requirement])
        for loop , index_of_rental_requirement in enumerate(index_of_rental_requirement_list):
            past_select_rental_list.append(rental_search_method_list[index_of_rental_requirement])

        return render_template(
            "schedule_search.html" ,
            past_select_solding_list = past_select_solding_list ,
            past_select_rental_list = past_select_rental_list ,
            solding_search_method_list = solding_search_method_list ,
            rental_search_method_list = rental_search_method_list ,
            login_flag = login_flag ,
        )
    else:
        return render_template(
            "schedule_search.html" ,
            login_flag = login_flag ,
        )


@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    global reins_sraper , solding_search_method_list , rental_search_method_list

    if request.method == 'POST':
        select_solding_list = []
        select_rental_list = []

        try:
            select_solding_list = request.form.getlist('select_solding')
            if select_solding_list == []:
                select_solding_list = [""]
            print(f"select_solding_list : ")
            print(select_solding_list)
            print()
            
        except:
            select_solding_list = [""]
        try:
            select_rental_list = request.form.getlist('select_rental')
            if select_rental_list == []:
                select_rental_list = [""]
            print(f"select_rental_list : ")
            print(select_rental_list)
            print()
        except:
            select_rental_list = [""]

        #  選択されなかった検索方法は０が返ってくる
        index_of_solding_requirement_list = []
        index_of_rental_requirement_list = []
        for select_solding in select_solding_list:
            index_of_solding_requirement = solding_search_method_list.index(select_solding)
            if select_solding == "":
                index_of_solding_requirement = 0
            index_of_solding_requirement_list.append(index_of_solding_requirement)
        for select_rental in select_rental_list:
            index_of_rental_requirement = rental_search_method_list.index(select_rental)
            if select_rental == "":
                index_of_rental_requirement = 0
            index_of_rental_requirement_list.append(index_of_rental_requirement)

        # Excelファイルの検索方法と条件を書き換える
        index_of_search_requirement_list = []
        index_of_search_requirement_list.append(index_of_solding_requirement_list)
        index_of_search_requirement_list.append(index_of_rental_requirement_list)
        ec.update_search_excel_file(search_method_excel_path , index_of_search_requirement_list)

        # S3上のcsvファイルを更新
        manipulate_s3.s3_file_upload(search_method_excel_path)

        return render_template(
            "result_search.html" ,
            select_solding_list = select_solding_list ,
            select_rental_list = select_rental_list ,
            index_of_search_requirement_list = index_of_search_requirement_list ,
        )
    


@app.route('/schedule_mail', methods=['GET', 'POST'])
def schedule_mail():
    global receive_mail_list
    if request.method == 'POST':
        # フォームから変更されたメールのリストを取得
        receive_mail_list_str = request.form['mail_list']
        receive_mail_list = re.split(r'\s+', receive_mail_list_str.strip())
        print(f"変更後 : ")
        print(receive_mail_list)
        # Excelファイルに変更
        ec.mail_list_to_excel(receive_mail_list , mail_excel_path)
        time.sleep(2)
        # S3上のExcelファイルを更新
        manipulate_s3.s3_file_upload(mail_excel_path)
        time.sleep(2)

        # 再びページを表示
        receive_mail_list , cc_mail_list , from_email , \
            from_email_smtp_password = ec.mail_list_from_excel(mail_excel_path)
        print(f"更新後 : ")
        print(receive_mail_list)
        receive_mail_list_str = "\n".join(receive_mail_list)
        return render_template(
            "schedule_mail.html" ,
            receive_mail_list_str = receive_mail_list_str ,
            from_email = from_email ,
            from_email_smtp_password = from_email_smtp_password ,
        )
    
    # メールアドレスのExcelファイルをS3から取得
    manipulate_s3.s3_file_download(local_upload_path = mail_excel_path)
    time.sleep(2)

    # Excelファイルからメールアドレスをリストで抽出
    receive_mail_list , cc_mail_list , from_email , \
        from_email_smtp_password = ec.mail_list_from_excel(mail_excel_path)
    print(f"変更前 : ")
    print(receive_mail_list)
    receive_mail_list_str = "\n".join(receive_mail_list)
    return render_template(
        "schedule_mail.html" ,
        receive_mail_list_str = receive_mail_list_str ,
        from_email = from_email ,
        from_email_smtp_password = from_email_smtp_password ,
    )




@app.route('/csv_download')
def csv_download():
    return send_file(output_reins_csv_path , as_attachment=True)

@app.route('/excel_download')
def excel_download():
    return send_file(output_reins_excel_path , as_attachment=True)



if __name__ == "__main__":
    port_number = 8810
    app.run(port = port_number , debug=True)




