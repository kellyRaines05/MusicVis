# downloads youtube clips according to a start and end timestamp

import yt_dlp

def download_clips():
    clip_times = {
        "https://www.youtube.com/watch?v=ZQJf0TwDjlg": {"start": 60, "end": 77, "title": "1"}, "https://www.youtube.com/watch?v=XZga5c9aJlQ": {"start": 14, "end": 33, "title": "2"}, "https://www.youtube.com/watch?v=nt8rQxjAQhE": {"start": 26, "end": 45, "title": "3"}, "https://www.youtube.com/watch?v=w7Cm74nDhac": {"start": 20, "end": 38, "title": "4"}, "https://www.youtube.com/watch?v=VyIL82TmnEE": {"start": 83, "end": 96, "title": "5"},
        "https://www.youtube.com/watch?v=R2hkdKVJSJ0`1": {"start": 126, "end": 146, "title": "6_1"}, "https://www.youtube.com/watch?v=R2hkdKVJSJ0`2": {"start": 162, "end": 182, "title": "6_2"}, "https://www.youtube.com/watch?v=R2hkdKVJSJ0`3": {"start": 183, "end": 201, "title": "6_3"}, "https://www.youtube.com/watch?v=YyknBTm_YyM": {"start": 129, "end": 149, "title": "7"}, "https://youtu.be/8QrpzphrQ7s?si=_j562BtdbjgqUEhX": {"start": 71, "end": 82, "title": "8"},
        "https://www.youtube.com/watch?v=UgSHUZvs8jg": {"start": 107, "end": 126, "title": "9"}, "https://www.youtube.com/watch?v=-mRn9chmRAY`1": {"start": 124, "end": 140, "title": "10_1"}, "https://www.youtube.com/watch?v=-mRn9chmRAY`2": {"start": 174, "end": 193, "title": "10_2"}, "https://www.youtube.com/watch?v=bXlEhvMNidg": {"start": 55, "end": 75, "title": "11"}, "https://www.youtube.com/watch?v=VmFmAvwO1pE": {"start": 263, "end": 281, "title": "12"},
        "https://www.youtube.com/watch?v=qpbX7SbXOtU": {"start": 92, "end": 111, "title": "13"}, "https://www.youtube.com/watch?v=mJ_fkw5j-t0`1": {"start": 97, "end": 110, "title": "14_1"}, "https://www.youtube.com/watch?v=mJ_fkw5j-t0`2": {"start": 171, "end": 185, "title": "14_2"}, "https://www.youtube.com/watch?v=Yh36PaE-Pf0": {"start": 179, "end": 192, "title": "15"}, "https://www.youtube.com/watch?v=MJedvm2TE8o": {"start": 75, "end": 85, "title": "16"},
        "https://www.youtube.com/watch?v=eFhMSV8Jjk4": {"start": 128, "end": 148, "title": "17"}, "https://www.youtube.com/watch?v=cQKGUgOfD8U": {"start": 92, "end": 109, "title": "18"}, "https://youtu.be/NH-GAwLAO30?si=0m4y7rg9dtiuL8Sh": {"start": 32, "end": 50, "title": "19"}, "https://www.youtube.com/watch?v=n8X9_MgEdCg": {"start": 90, "end": 110, "title": "20"}, "https://www.youtube.com/watch?v=cVukkhUI-xM`1": {"start": 74, "end": 94, "title": "21_1"},
        "https://www.youtube.com/watch?v=cVukkhUI-xM`2": {"start": 218, "end": 238, "title": "21_2"}, "https://www.youtube.com/watch?v=cVukkhUI-xM`3": {"start": 447, "end": 461, "title": "21_3"}, "https://www.youtube.com/watch?v=-dAv10E4f5k": {"start": 80, "end": 97, "title": "22"}, "https://www.youtube.com/watch?v=juje1eBtEnw": {"start": 37, "end": 49, "title": "23"}, "https://www.youtube.com/watch?v=7AYtfNgnRxI": {"start": 112, "end": 130, "title": "24"},
        "https://www.youtube.com/watch?v=1fMi247Klsk": {"start": 32, "end": 52, "title": "25"}, "https://www.youtube.com/watch?v=PzBKlcYaKNg": {"start": 126, "end": 145, "title": "26"}, "https://www.youtube.com/watch?v=mkqEmQsPzfA": {"start": 60, "end": 77, "title": "27"}, "https://www.youtube.com/watch?v=Uce4YoxDAIE": {"start": 89, "end": 111, "title": "28"}, "https://www.youtube.com/watch?v=BlnVP2_dIb4": {"start": 52, "end": 75, "title": "29"},
        "https://www.youtube.com/watch?v=tsmPCi7NKrg": {"start": 132, "end": 147, "title": "30"}, "https://www.youtube.com/watch?v=sHCT2TCaN8E": {"start": 117, "end": 133, "title": "31"}, "https://www.youtube.com/watch?v=gEhuGPXxRrA": {"start": 108, "end": 128, "title": "32"}, "https://www.youtube.com/watch?v=O4irXQhgMqg": {"start": 110, "end": 123, "title": "33"}, "https://www.youtube.com/watch?v=FcZfHJc9GXw": {"start": 125, "end": 145, "title": "34"},
        "https://www.youtube.com/watch?v=IaLqkeKx814": {"start": 124, "end": 139, "title": "35"}, "https://www.youtube.com/watch?v=d_HlPboLRL8": {"start": 109, "end": 129, "title": "36"}, "https://www.youtube.com/watch?v=5DznlKlIrbo": {"start": 83, "end": 101, "title": "37"}, "https://www.youtube.com/watch?v=3jfI-z__GY0": {"start": 103, "end": 116, "title": "38"}, "https://www.youtube.com/watch?v=_9myt3qKHkY": {"start": 60, "end": 78, "title": "39"},
        "https://www.youtube.com/watch?v=vwPCOU8V4kU": {"start": 19, "end": 37, "title": "40"}, "https://www.youtube.com/watch?v=R8ALe-nVzd8": {"start": 105, "end": 124, "title": "41"}, "https://www.youtube.com/watch?v=WSEpDD8j6-c": {"start": 96, "end": 116, "title": "42"}, "https://www.youtube.com/watch?v=oJuGlqO85YI": {"start": 117, "end": 139, "title": "43"}, "https://www.youtube.com/watch?v=z2_Lrg6rRks": {"start": 123, "end": 135, "title": "44"},
        "https://www.youtube.com/watch?v=uWoYIOcOpwU": {"start": 110, "end": 129, "title": "45"}, "https://www.youtube.com/watch?v=eif_8yA2WhA": {"start": 86, "end": 103, "title": "46"}, "https://www.youtube.com/watch?v=f1e8Ok4BmeU": {"start": 49, "end": 69, "title": "47"}, "https://www.youtube.com/watch?v=u-GmuvAVKsE": {"start": 98, "end": 114, "title": "48"}, "https://www.youtube.com/watch?v=pI8TZuxIZCc": {"start": 74, "end": 85, "title": "49"},
        "https://www.youtube.com/watch?v=68fgmFx5acg": {"start": 82, "end": 95, "title": "50"}, "https://www.youtube.com/watch?v=0nPI4_GLkAM": {"start": 60, "end": 80, "title": "51"}, "https://www.youtube.com/watch?v=6_Ab6ybbzFw": {"start": 133, "end": 150, "title": "52"}, "https://www.youtube.com/watch?v=J8Hik8pGlQI": {"start": 129, "end": 145, "title": "53"}, "https://www.youtube.com/watch?v=d1kWg-kNx3k": {"start": 88, "end": 105, "title": "54"},
        "https://www.youtube.com/watch?v=KgbY_hvI11o": {"start": 99, "end": 109, "title": "55"}, "https://www.youtube.com/watch?v=HOGQPMmKB7Y": {"start": 150, "end": 168, "title": "56"}, "https://www.youtube.com/watch?v=1QH7Aw5pA30": {"start": 136, "end": 156, "title": "57"}, "https://www.youtube.com/watch?v=O8Zei-9o9cg": {"start": 89, "end": 110, "title": "58"}, "https://www.youtube.com/watch?v=CAMWdvo71ls": {"start": 175, "end": 195, "title": "59"},
        "https://www.youtube.com/watch?v=t5D7XTHWAdw": {"start": 148, "end": 168, "title": "60"}, "https://www.youtube.com/watch?v=_om0W6xzQd8": {"start": 90, "end": 111, "title": "61"}, "https://www.youtube.com/watch?v=bFEP26jCtsQ": {"start": 120, "end": 135, "title": "62"}, "https://www.youtube.com/watch?v=HGSAcjPj2YQ": {"start": 65, "end": 75, "title": "63"}, "https://www.youtube.com/watch?v=U8BlNEKq0r8`1": {"start": 144, "end": 154, "title": "64_1"},
        "https://www.youtube.com/watch?v=U8BlNEKq0r8`2": {"start": 182, "end": 197, "title": "64_2"}, "https://www.youtube.com/watch?v=KhJrWWbj6aw": {"start": 132, "end": 152, "title": "65"}, "https://www.youtube.com/watch?v=mJ1N7-HyH1A": {"start": 132, "end": 151, "title": "66"}, "https://www.youtube.com/watch?v=v-WcMQbXbKY": {"start": 145, "end": 162, "title": "67"}, "https://www.youtube.com/watch?v=dgapVye0Ktw": {"start": 131, "end": 150, "title": "68"},
        "https://youtu.be/Uggs5e7eAYo?si=u0SNIYpO4MEzJlXm": {"start": 63, "end": 81, "title": "69"}, "https://www.youtube.com/watch?v=35nV_M3asRs`1": {"start": 112, "end": 125, "title": "70_1"}, "https://www.youtube.com/watch?v=35nV_M3asRs`2": {"start": 138, "end": 151, "title": "70_2"}, "https://www.youtube.com/watch?v=3P7aRlbBnrg": {"start": 115, "end": 128, "title": "71"}, "https://www.youtube.com/watch?v=5BMnuvtdw1s": {"start": 84, "end": 97, "title": "72"}, "https://www.youtube.com/watch?v=Sw1Flgub9s8": {"start": 138, "end": 155, "title": "73"},
        "https://www.youtube.com/watch?v=kD6TZpDaWr8": {"start": 74, "end": 92, "title": "74"}, "https://www.youtube.com/watch?v=IbbhN4zFDfE": {"start": 72, "end": 86, "title": "75"}, "https://www.youtube.com/watch?v=y4ZnV72Zco8": {"start": 115, "end": 135, "title": "76"}, "https://www.youtube.com/watch?v=iJAxeafvn8Y": {"start": 42, "end": 56, "title": "77"}, "https://www.youtube.com/watch?v=ohI8LKYlIyc": {"start": 60, "end": 73, "title": "78"},
        "https://www.youtube.com/watch?v=ATPulcGQ2SE": {"start": 130, "end": 155, "title": "79"}, "https://www.youtube.com/watch?v=q07EmkvztQM": {"start": 180, "end": 194, "title": "80"}, "https://www.youtube.com/watch?v=6THHrPyZQuQ": {"start": 120, "end": 151, "title": "81"}, "https://www.youtube.com/watch?v=um8-0zDtdpQ": {"start": 110, "end": 134, "title": "82"}, "https://www.youtube.com/watch?v=lUsBM7cS4lY": {"start": 178, "end": 198, "title": "83"},
        "https://www.youtube.com/watch?v=0JMdXFHo5SY": {"start": 110, "end": 127, "title": "84"}, "https://www.youtube.com/watch?v=poKI_MY0Bkw": {"start": 46, "end": 67, "title": "85"}, "https://www.youtube.com/watch?v=wMBNpVQ0k_k": {"start": 74, "end": 87, "title": "86"}, "https://www.youtube.com/watch?v=KTsAmq9h7iM": {"start": 126, "end": 142, "title": "87"}, "https://www.youtube.com/watch?v=R_RAWjqdgTs": {"start": 36, "end": 49, "title": "88"},
        "https://www.youtube.com/watch?v=Q1Euvef0UX0": {"start": 130, "end": 141, "title": "89"}, "https://www.youtube.com/watch?v=1mAPHxL8KgM`1": {"start": 25, "end": 35, "title": "90_1"}, "https://www.youtube.com/watch?v=1mAPHxL8KgM`2": {"start": 70, "end": 81, "title": "90_2"}, "https://www.youtube.com/watch?v=xA1TJrx5ZI8": {"start": 90, "end": 112, "title": "91"}, "https://www.youtube.com/watch?v=Jlq694r6OmA": {"start": 67, "end": 84, "title": "92"},
        "https://www.youtube.com/watch?v=KaLFZj3wPsc": {"start": 32, "end": 46, "title": "93"}, "https://www.youtube.com/watch?v=aXsLlOPwe48": {"start": 72, "end": 107, "title": "94"}, "https://www.youtube.com/watch?v=YUH9jD__qHY": {"start": 128, "end": 146, "title": "95"}, "https://www.youtube.com/watch?v=vGGbp88ziXU": {"start": 104, "end": 118, "title": "96"}, "https://www.youtube.com/watch?v=g3ENX3aHlqU": {"start": 138, "end": 158, "title": "97"},
        "https://www.youtube.com/watch?v=hjghAcOdGjQ": {"start": 87, "end": 98, "title": "98"}, "https://www.youtube.com/watch?v=6CfRJSKk2Ls": {"start": 65, "end": 75, "title": "99"}, "https://www.youtube.com/watch?v=-JWkQbRNtjs": {"start": 105, "end": 128, "title": "100"}
    }

    for link in clip_times:
        link_real = link.split("`")
        start = clip_times[link]["start"]
        end = clip_times[link]["end"]
        title = clip_times[link]["title"]
        title = str(title).zfill(3)
        download_video_clip(link_real[0], start, end, title)

def download_video_clip(video_url, start, end, title):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": f"s{title}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "postprocessor_args": [
            "-ss", str(start),
            "-to", str(end)
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == "__main__":
    download_clips()
