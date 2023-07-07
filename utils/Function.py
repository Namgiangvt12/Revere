from urllib.parse import urlparse, parse_qs

import requests
import os
from tqdm import tqdm
from datetime import datetime
import pdfkit
import subprocess
from google.cloud import storage
import json


def getPath(save_path):
    current_directory = os.getcwd()
    folder_name = os.path.basename(current_directory)

    if folder_name == "Revere":
        file_path = os.path.join(current_directory, save_path)
    else:
        file_path = os.path.join(os.path.dirname(os.getcwd()), save_path)
    return file_path


nameBucket = "reveredefault"
ffmpeg_path = getPath("") + r'\ffmpeg\bin\ffmpeg.exe'
path_to_wkhtmltopdf = getPath("") + r'\wkhtmltopdf\bin\wkhtmltopdf.exe'

config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)


def download_minutes(url, save_path, name, headers, date):
    file_path = getPath("data")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(f"{file_path}/Minutes/{name}.pdf", 'wb') as file:
            file.write(response.content)
        print("Minutes downloaded successfully!")
    else:
        print("Failed to download Minutes.")
    # upload_file_to_bucket(nameBucket, f"{file_path}/Minutes/{name}.pdf", f"{name}.pdf", save_path, date)


def download_pdf(url, save_path, name, headers, date):
    file_path = getPath("data")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(f"{file_path}\Agendas\{name}.pdf", 'wb') as file:
            file.write(response.content)
        print("Agendas downloaded successfully!")
    else:
        print("Failed to download Agendas .")
    # upload_file_to_bucket(nameBucket, f"{file_path}/Agendas/{name}.pdf", f"{name}.pdf", save_path, date)


def download_video(url, save_path, name, date):
    file_path = getPath("data")
    response = requests.get(url, stream=True)
    with open(f"{file_path}/Media/{name}.mp4", 'wb') as file, tqdm(
            total=int(response.headers.get('content-length', 0)), unit='B', unit_scale=True, unit_divisor=1024
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress_bar.update(len(chunk))
    print("Mp4 is downloaded successfully")
    # upload_file_to_bucket(nameBucket, f"{file_path}/Mp3_Video/{name}.mp4", f"{name}.mp4", save_path, "media", date)


def download_mp3(url, save_path, name, date):
    file_path = getPath("data")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(f"{file_path}/Media/{name}.mp3", 'wb') as file, tqdm(
                total=int(response.headers.get('content-length', 0)), unit='B', unit_scale=True,
                unit_divisor=1024) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        print("MP3 downloaded successfully!")
    else:
        print("Failed to download MP3.")
    # upload_file_to_bucket(nameBucket, f"{file_path}/Media/{name}.mp3", f"{name}.mp3", save_path, date)


def convert_date(fromStr, typeofstr):
    datetime_obj = datetime.strptime(fromStr, typeofstr)
    formatte_date = datetime_obj.strftime("%b %d, %Y")
    formatted_date = datetime.strptime(formatte_date, "%b %d, %Y")
    return formatted_date


def download_htmltopdf(url, save_path, name, headers, type, date):
    file_path = getPath("data")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        try:
            pdfkit.from_string(html_content, output_path=f"{file_path}/{type}/{name}.pdf", configuration=config)
            print(f"{type} downloaded successfully")
            #upload_file_to_bucket(nameBucket, f"{file_path}/{type}/{name}.pdf", f"{name}.pdf", save_path, date)
        except OSError as e:
            print("Lỗi OSError:", str(e))
        except Exception as e:
            print("Lỗi:", str(e))
    else:
        print("Lỗi khi tải file.")


def Download_videom3u8(url, save_path, name, header):
    file_path = getPath("data")
    subprocess.call([ffmpeg_path, '-i', url, f'{file_path}/Media/{name}.mp4'])
    print()


def nameString(datetime_):
    string_date = str(datetime_.month) + "_" + str(datetime_.day) + "_" + str(datetime_.year)
    return string_date


def upload_file_to_bucket(bucket_name, file_path, destination_blob_name, location, date):
    storage_client = storage.Client(project="revere-391311")
    bucket = storage_client.bucket(bucket_name)
    blob_name = f"CA/{location}/{date}/{destination_blob_name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to bucket {bucket_name} by name : {blob_name}.")
    deleteFile(file_path)


def deleteFile(url):
    try:
        if os.path.exists(url):
            os.remove(url)
            print("Deleted file in local")
        else:
            print("Tệp tin không tồn tại.")
    except OSError as e:
        print(f"Lỗi: {e.filename} - {e.strerror}.")



def write_json(location_value, new_id):
    file_path = getPath("data") + "/data.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    for item in data:
        if item["location"] == location_value:
            existing_ids = item["ID"]
            if new_id not in existing_ids:
                existing_ids.append(new_id)
            break
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    return True

def check_exist(location_value, new_id) :
    added = 0
    file_path = getPath("data") + "/data.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    found_location = False
    for item in data:
        if item["location"] == location_value:
            existing_ids = item["ID"]
            if new_id not in existing_ids:
                added = 0
            else:
                added = 1
            found_location = True
            break
    if not found_location:
        new_item = {
            "location": location_value,
            "ID": []
        }
        added = 0
        data.append(new_item)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    return added != 1


def getID(url, Values):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params.get(Values)[0]
    return int(id_value)

def check_empty(text_) :
    if text_ == "" : return "N/A"
def convert_to_time_for_push(text_,style) :
    time_object = datetime.strptime(text_, style)
    formatted_time = time_object.strftime("%H:%M")
    return formatted_time

def convert_to_date_for_push(text_,style) :
    time_object = datetime.strptime(text_, style)
    formatted_date = time_object.strftime("%Y-%m-%d")
    return formatted_date
