import os, re
import requests
from tqdm import tqdm
from urllib.parse import urljoin

# Settings
download_dir = "download_papers"
os.makedirs(download_dir, exist_ok=True)

with open('paper.txt', 'r') as txt:
    paper_list = [paper.strip('\n') for paper in txt.readlines()]

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
})

headers = {
    "authority": "sci-hub.se",
    "method": "POST",
    "path": "/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-US,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
    "cache-control": "max-age=0",
    "origin": "https://sci-hub.se",
    "referer": "https://sci-hub.se/",
    "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

failure_txt = open('failure_download.txt', 'w')

for paper_name in tqdm(paper_list):
    try:
        data = {"request": paper_name}
        response = session.post("https://sci-hub.se/", headers=headers, data=data, allow_redirects=False)
        location = response.headers.get('Location')
        
        redirect_response = session.get(location, headers=headers)
        pdf_url = re.findall(r'<embed type="application/pdf" src="([^"]+)"', redirect_response.text)[0]

        pdf_url = urljoin("https://sci-hub.se/", pdf_url)
        pdf_response = requests.get(pdf_url, headers=headers)

        save_name = paper_name.replace(":", " ") + '.pdf'
        save_path = os.path.join(download_dir, save_name)

        with open(save_path, 'wb') as fp:
            fp.write(pdf_response.content)

        tqdm.write(f"[SUCCESS] {paper_name} \t {location}")
    except:
        message = f"[NOT AVAILABLE] {paper_name} \t {location}"
        tqdm.write(message)
        failure_txt.write(message + '\n')
        failure_txt.flush()

failure_txt.close()