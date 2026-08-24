import os
import subprocess

caption = """Cada lanche com a sua personalidade! \U0001F354\U0001F525 Dá uma olhada na variedade que a GM prepara pra você, sempre fresquinho, sempre com capricho. Qual desses é a sua cara?

\U0001F4CD GM Hamburgueria Artesanal
⏰ Delivery: todos os dias, das 11h às 01h
\U0001F449 Peça já o seu!"""

photo_urls = [
    "https://scontent-hkg4-1.xx.fbcdn.net/v/t39.30808-6/783985399_1503779555098150_2303816187187936628_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=e5c1b6&_nc_ohc=pMF2InxOg6YQ7kNvwHGaH2y&_nc_oc=AdoUbHPHWunSxWnqRzGydsf__1tuVYaut3gbV9FiwDYeKIGM9DVyH7sq8c8QUt6VIO8&_nc_zt=23&_nc_ht=scontent-hkg4-1.xx&edm=AMAeTUEEAAAA&_nc_gid=gIe9Dx3bPhoCAkLnCcrxYA&_nc_tpa=Q5bMBQIX4plymOIIVE7m-eETDROFWityUuxVprRitU9JJtAIJ_w01vIXEQS3jKT_GNuvXnF27QT5uuqt9A&oh=00_AQFkNpNSKeF7mYS7-xytpQOmTQ04NxewV5N27yMoEcT73w&oe=6A928D38",
    "https://scontent-hkg1-2.xx.fbcdn.net/v/t39.30808-6/786141135_1503779601764812_1728335163961591148_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=e5c1b6&_nc_ohc=1gXknrHp-N0Q7kNvwEKf6dr&_nc_oc=AdrO6ncA3NoUCS6YlcTxrQ2X6hL-Xn45JrsbaC-Y5Av8fq__AYF6QAzOND5MT2DbI_A&_nc_zt=23&_nc_ht=scontent-hkg1-2.xx&edm=AMAeTUEEAAAA&_nc_gid=Jjid6WxWgrpDde2vHK7XEQ&_nc_tpa=Q5bMBQIAehDoY3_QMzl5c0vxN4qqNkNv5e36U0caNt7Ppky_WwsDqbkSMcBX6MpKigOFCYkhCHinCEF8Zg&oh=00_AQHUzYl4pTZMvHedsXyXtwQHlDmym6tBbSS_Sj7EbINBqQ&oe=6A929177",
    "https://scontent-hkg1-2.xx.fbcdn.net/v/t39.30808-6/786242843_1503779661764806_470969273891836816_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=e5c1b6&_nc_ohc=vUG1KCzzQtMQ7kNvwFdgb8J&_nc_oc=AdqF7Oeh9NfeJon6zG3Bdpa7VrkvcUWptPC6M_J73Vvrmu-O8YbE7UZWkG3pdf5UEJY&_nc_zt=23&_nc_ht=scontent-hkg1-2.xx&edm=AMAeTUEEAAAA&_nc_gid=Vlht-iutAalSTQeQZf_D_A&_nc_tpa=Q5bMBQJchbfL9JHZwNBHZ2hxUV6a9EoTz9AtUJiaiRSmojZZnnpo6WRLs2-Xdnx_NCwtshwlfhTCtjVdYA&oh=00_AQHY_Q1fG3v81MjgnMU1iHBKdPvNkAbNsoEJIDDkdfM1hw&oe=6A928EFD",
    "https://scontent-hkg1-1.xx.fbcdn.net/v/t39.30808-6/786470454_1503779701764802_5518642892162208234_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=e5c1b6&_nc_ohc=_7Vcs7fkJpQQ7kNvwGiyfox&_nc_oc=Adq_nESiBcIpJA2Qfb_kAMgwfmKLe8Q7GNsowxT_aRp3nH_V8hV05I-L6FbRrqsDB3M&_nc_zt=23&_nc_ht=scontent-hkg1-1.xx&edm=AMAeTUEEAAAA&_nc_gid=lCWkjOIolAbN_4-zV1EXwQ&_nc_tpa=Q5bMBQL3kE4-noW7tb381dTWw6kc17eZYhQDXfOG25W4MvP99Npj2JoAT88MfFb_P_QtL2utafOpFVgmiQ&oh=00_AQEWLVPnwZeFx9D1j3Yq4gq_uEkwty4z0hpBKBMEIqpsJw&oe=6A927AD5",
    "https://scontent-hkg1-1.xx.fbcdn.net/v/t39.30808-6/786167164_1503779745098131_3354832222780822497_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=e5c1b6&_nc_ohc=bptPMpJoTgcQ7kNvwHSeC5i&_nc_oc=AdpQmoO54S9sbDxoJPjdlMWFXZKKylfn0dUaaIlzjp3PdQrriLyPPrr4MAI0lbKEQP4&_nc_zt=23&_nc_ht=scontent-hkg1-1.xx&edm=AMAeTUEEAAAA&_nc_gid=c-4DfyfNGdjmY-g55xvc8Q&_nc_tpa=Q5bMBQIWGBDf9Ag79AOtqfGpFs7oGdQpJLx5sb7dkuGGsysWj1NdShiczOMxxU79FoXRW2YBbnMNzXhPrw&oh=00_AQFd2uZ1gUqHHErph3bTJizApgMHGWdLZZi42h7aT9m4Ig&oe=6A929DC5",
]

caption_path = "catchup_caption_gm.txt"
with open(caption_path, "w", encoding="utf-8") as f:
    f.write(caption)

import time
time.sleep(20)  # gives Meta a moment to finish processing the photos before we retry publish

cmd = ["bash", "scripts/post_instagram.sh", caption_path] + photo_urls
print("Chamando:", cmd)
result = subprocess.run(cmd)
raise SystemExit(result.returncode)
