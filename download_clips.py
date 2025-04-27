# downloads youtube clips according to a start and end timestamp

import yt_dlp

def download_clips(video_links):
    clip_times = {
        "https://www.youtube.com/watch?v=ZQJf0TwDjlg": {"start": 60, "end": 77}, "https://www.youtube.com/watch?v=XZga5c9aJlQ": {"start": 14, "end": 33}, "https://www.youtube.com/watch?v=nt8rQxjAQhE": {"start": 26, "end": 45}, "https://www.youtube.com/watch?v=w7Cm74nDhac": {"start": 20, "end": 38}, "https://www.youtube.com/watch?v=VyIL82TmnEE": {"start": 83, "end": 96},
        "https://www.youtube.com/watch?v=R2hkdKVJSJ0": {"start": 126, "end": 146}, "https://www.youtube.com/watch?v=R2hkdKVJSJ0": {"start": 162, "end": 182}, "https://www.youtube.com/watch?v=R2hkdKVJSJ0": {"start": 183, "end": 201}, "https://www.youtube.com/watch?v=YyknBTm_YyM": {"start": 129, "end": 149}, "https://www.youtube.com/watch?v=MsHuoKN63Y4": {"start": 71, "end": 82},
        "https://www.youtube.com/watch?v=UgSHUZvs8jg": {"start": 107, "end": 126}, "https://www.youtube.com/watch?v=-mRn9chmRAY": {"start": 124, "end": 140}, "https://www.youtube.com/watch?v=-mRn9chmRAY": {"start": 174, "end": 193}, "https://www.youtube.com/watch?v=bXlEhvMNidg": {"start": 55, "end": 75}, "https://www.youtube.com/watch?v=VmFmAvwO1pE": {"start": 263, "end": 281},
        "https://www.youtube.com/watch?v=qpbX7SbXOtU": {"start": 92, "end": 111}, "https://www.youtube.com/watch?v=mJ_fkw5j-t0": {"start": 97, "end": 110}, "https://www.youtube.com/watch?v=mJ_fkw5j-t0": {"start": 171, "end": 185}, "https://www.youtube.com/watch?v=Yh36PaE-Pf0": {"start": 179, "end": 192}, "https://www.youtube.com/watch?v=MJedvm2TE8o": {"start": 75, "end": 85},
        "https://www.youtube.com/watch?v=eFhMSV8Jjk4": {"start": 128, "end": 148}, "https://www.youtube.com/watch?v=cQKGUgOfD8U": {"start": 92, "end": 109}, "https://www.youtube.com/watch?v=YZ3XjVVNagU": {"start": 32, "end": 50}, "https://www.youtube.com/watch?v=n8X9_MgEdCg": {"start": 90, "end": 110}, "https://www.youtube.com/watch?v=cVukkhUI-xM": {"start": 74, "end": 94},
        "https://www.youtube.com/watch?v=cVukkhUI-xM": {"start": 218, "end": 238}, "https://www.youtube.com/watch?v=cVukkhUI-xM": {"start": 447, "end": 461}, "https://www.youtube.com/watch?v=-dAv10E4f5k": {"start": 80, "end": 97}, "https://www.youtube.com/watch?v=juje1eBtEnw": {"start": 37, "end": 49}, "https://www.youtube.com/watch?v=7AYtfNgnRxI": {"start": 112, "end": 130},
        "https://www.youtube.com/watch?v=1fMi247Klsk": {"start": 32, "end": 52}, "https://www.youtube.com/watch?v=PzBKlcYaKNg": {"start": 126, "end": 145}, "https://www.youtube.com/watch?v=mkqEmQsPzfA": {"start": 60, "end": 77}, "https://www.youtube.com/watch?v=Uce4YoxDAIE": {"start": 89, "end": 111} , "https://www.youtube.com/watch?v=BlnVP2_dIb4": {"start": 52, "end": 75},
        "https://www.youtube.com/watch?v=tsmPCi7NKrg": {"start": 132, "end": 147}, "https://www.youtube.com/watch?v=sHCT2TCaN8E": {"start": 117, "end": 133}, "https://www.youtube.com/watch?v=gEhuGPXxRrA": {"start": 108, "end": 128}, "https://www.youtube.com/watch?v=O4irXQhgMqg": {"start": 110, "end": 123}, "https://www.youtube.com/watch?v=FcZfHJc9GXw": {"start": 125, "end": 145},
        "https://www.youtube.com/watch?v=IaLqkeKx814": {"start": 124, "end": 139}, "https://www.youtube.com/watch?v=d_HlPboLRL8": {"start": 109, "end": 129}, "https://www.youtube.com/watch?v=5DznlKlIrbo": {"start": 83, "end": 101}, "https://www.youtube.com/watch?v=3jfI-z__GY0": {"start": 103, "end": 116}, "https://www.youtube.com/watch?v=_9myt3qKHkY": {"start": 60, "end": 78},
        "https://www.youtube.com/watch?v=vwPCOU8V4kU": {"start": 19, "end": 37}, "https://www.youtube.com/watch?v=R8ALe-nVzd8": {"start": 105, "end": 124}, "https://www.youtube.com/watch?v=WSEpDD8j6-c": {"start": 96, "end": 116}, "https://www.youtube.com/watch?v=oJuGlqO85YI": {"start": 117, "end": 139}, "https://www.youtube.com/watch?v=z2_Lrg6rRks": {"start": 123, "end": 135},
        "https://www.youtube.com/watch?v=uWoYIOcOpwU": {"start": 110, "end": 129}, "https://www.youtube.com/watch?v=eif_8yA2WhA": {"start": 86, "end": 103}, "https://www.youtube.com/watch?v=f1e8Ok4BmeU": {"start": 49, "end": 69}, "https://www.youtube.com/watch?v=u-GmuvAVKsE": {"start": 98, "end": 114}, "https://www.youtube.com/watch?v=pI8TZuxIZCc": {"start": 74, "end": 95},
        "https://www.youtube.com/watch?v=68fgmFx5acg": {"start": 82, "end": 95}, "https://www.youtube.com/watch?v=0nPI4_GLkAM": {"start": 60, "end": 80}, "https://www.youtube.com/watch?v=6_Ab6ybbzFw": {"start": 133, "end": 150}, "https://www.youtube.com/watch?v=J8Hik8pGlQI": {"start": 129, "end": 145}, "https://www.youtube.com/watch?v=d1kWg-kNx3k": {"start": 88, "end": 105},
        "https://www.youtube.com/watch?v=KgbY_hvI11o": {"start": 99, "end": 109}, "https://www.youtube.com/watch?v=HOGQPMmKB7Y": {"start": 150, "end": 168}, "https://www.youtube.com/watch?v=1QH7Aw5pA30": {"start": 136, "end": 156}, "https://www.youtube.com/watch?v=O8Zei-9o9cg": {"start": 89, "end": 110}, "https://www.youtube.com/watch?v=CAMWdvo71ls": {"start": 175, "end": 195},
        "https://www.youtube.com/watch?v=t5D7XTHWAdw": {"start": 148, "end": 168}, "https://www.youtube.com/watch?v=_om0W6xzQd8": {"start": 90, "end": 111}, "https://www.youtube.com/watch?v=bFEP26jCtsQ": {"start": 120, "end": 135}, "https://www.youtube.com/watch?v=HGSAcjPj2YQ": {"start": 65, "end": 75}, "https://www.youtube.com/watch?v=U8BlNEKq0r8": {"start": 144, "end": 154},
        "https://www.youtube.com/watch?v=U8BlNEKq0r8": {"start": 182, "end": 197}, "https://www.youtube.com/watch?v=KhJrWWbj6aw": {"start": 132, "end": 152}, "https://www.youtube.com/watch?v=mJ1N7-HyH1A": {"start": 132, "end": 151}, "https://www.youtube.com/watch?v=v-WcMQbXbKY": {"start": 145, "end": 162}, "https://www.youtube.com/watch?v=dgapVye0Ktw": {"start": 131, "end": 150},
        "https://www.youtube.com/watch?v=moR4uw-NWLY": {"start": 83, "end": 92}, "https://www.youtube.com/watch?v=35nV_M3asRs": {"start": 112, "end": 125}, "https://www.youtube.com/watch?v=3P7aRlbBnrg": {"start": 115, "end": 128}, "https://www.youtube.com/watch?v=5BMnuvtdw1s": {"start": 84, "end": 97}, "https://www.youtube.com/watch?v=Sw1Flgub9s8": {"start": 138, "end": 155},
        "https://www.youtube.com/watch?v=kD6TZpDaWr8": {"start": 74, "end": 92}, "https://www.youtube.com/watch?v=IbbhN4zFDfE": {"start": 72, "end": 86}, "https://www.youtube.com/watch?v=y4ZnV72Zco8": {"start": 115, "end": 135}, "https://www.youtube.com/watch?v=iJAxeafvn8Y": {"start": 42, "end": 56}, "https://www.youtube.com/watch?v=ohI8LKYlIyc": {"start": 60, "end": 73},
        "https://www.youtube.com/watch?v=ATPulcGQ2SE": {"start": 130, "end": 155}, "https://www.youtube.com/watch?v=q07EmkvztQM": {"start": 180, "end": 194}, "https://www.youtube.com/watch?v=6THHrPyZQuQ": {"start": 120, "end": 181}, "https://www.youtube.com/watch?v=um8-0zDtdpQ": {"start": 110, "end": 134}, "https://www.youtube.com/watch?v=lUsBM7cS4lY": {"start": 178, "end": 198},
        "https://www.youtube.com/watch?v=0JMdXFHo5SY": {"start": 110, "end": 127}, "https://www.youtube.com/watch?v=poKI_MY0Bkw": {"start": 46, "end": 67}, "https://www.youtube.com/watch?v=wMBNpVQ0k_k": {"start": 74, "end": 87}, "https://www.youtube.com/watch?v=KTsAmq9h7iM": {"start": 126, "end": 142}, "https://www.youtube.com/watch?v=R_RAWjqdgTs": {"start": 36, "end": 49},
        "https://www.youtube.com/watch?v=Q1Euvef0UX0": {"start": 130, "end": 151}, "https://www.youtube.com/watch?v=1mAPHxL8KgM": {"start": 25, "end": 35}, "https://www.youtube.com/watch?v=1mAPHxL8KgM": {"start": 70, "end": 91}, "https://www.youtube.com/watch?v=xA1TJrx5ZI8": {"start": 90, "end": 112}, "https://www.youtube.com/watch?v=Jlq694r6OmA": {"start": 67, "end": 94},
        "https://www.youtube.com/watch?v=KaLFZj3wPsc": {"start": 32, "end": 46}, "https://www.youtube.com/watch?v=aXsLlOPwe48": {"start": 72, "end": 107}, "https://www.youtube.com/watch?v=YUH9jD__qHY": {"start": 128, "end": 146}, "https://www.youtube.com/watch?v=vGGbp88ziXU": {"start": 104, "end": 118}, "https://www.youtube.com/watch?v=g3ENX3aHlqU": {"start": 138, "end": 158},
        "https://www.youtube.com/watch?v=hjghAcOdGjQ": {"start": 87, "end": 98}, "https://www.youtube.com/watch?v=6CfRJSKk2Ls": {"start": 65, "end": 75}, "https://www.youtube.com/watch?v=-JWkQbRNtjs": {"start": 105, "end": 128}
    }

    for link in video_links:
        if link in clip_times:
            start = clip_times[link]["start"]
            end = clip_times[link]["end"]
            download_video_clip(link, start, end)
        else:
            print(f"No start/end times specified for: {link}")

def download_video_clip(video_url, start, end):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "%(title)s_%(id)s_clip.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "postprocessor_args": [
            "-ss", str(start),
            "-to", str(end)
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == "__main__":
    youtube_links = [
        "https://www.youtube.com/watch?v=ZQJf0TwDjlg", "https://www.youtube.com/watch?v=XZga5c9aJlQ", "https://www.youtube.com/watch?v=nt8rQxjAQhE", "https://www.youtube.com/watch?v=w7Cm74nDhac", "https://www.youtube.com/watch?v=VyIL82TmnEE",
        "https://www.youtube.com/watch?v=R2hkdKVJSJ0", "https://www.youtube.com/watch?v=YyknBTm_YyM", "https://www.youtube.com/watch?v=MsHuoKN63Y4", "https://www.youtube.com/watch?v=UgSHUZvs8jg", "https://www.youtube.com/watch?v=-mRn9chmRAY",
        "https://www.youtube.com/watch?v=bXlEhvMNidg", "https://www.youtube.com/watch?v=VmFmAvwO1pE", "https://www.youtube.com/watch?v=qpbX7SbXOtU", "https://www.youtube.com/watch?v=mJ_fkw5j-t0", "https://www.youtube.com/watch?v=Yh36PaE-Pf0",
        "https://www.youtube.com/watch?v=MJedvm2TE8o", "https://www.youtube.com/watch?v=eFhMSV8Jjk4", "https://www.youtube.com/watch?v=cQKGUgOfD8U", "https://www.youtube.com/watch?v=YZ3XjVVNagU", "https://www.youtube.com/watch?v=n8X9_MgEdCg",
        "https://www.youtube.com/watch?v=cVukkhUI-xM", "https://www.youtube.com/watch?v=-dAv10E4f5k", "https://www.youtube.com/watch?v=juje1eBtEnw", "https://www.youtube.com/watch?v=7AYtfNgnRxI", "https://www.youtube.com/watch?v=1fMi247Klsk",
        "https://www.youtube.com/watch?v=PzBKlcYaKNg", "https://www.youtube.com/watch?v=mkqEmQsPzfA", "https://www.youtube.com/watch?v=Uce4YoxDAIE", "https://www.youtube.com/watch?v=BlnVP2_dIb4", "https://www.youtube.com/watch?v=tsmPCi7NKrg",
        "https://www.youtube.com/watch?v=sHCT2TCaN8E", "https://www.youtube.com/watch?v=gEhuGPXxRrA", "https://www.youtube.com/watch?v=O4irXQhgMqg", "https://www.youtube.com/watch?v=FcZfHJc9GXw", "https://www.youtube.com/watch?v=IaLqkeKx814",
        "https://www.youtube.com/watch?v=d_HlPboLRL8", "https://www.youtube.com/watch?v=5DznlKlIrbo", "https://www.youtube.com/watch?v=3jfI-z__GY0", "https://www.youtube.com/watch?v=_9myt3qKHkY", "https://www.youtube.com/watch?v=vwPCOU8V4kU",
        "https://www.youtube.com/watch?v=R8ALe-nVzd8", "https://www.youtube.com/watch?v=WSEpDD8j6-c", "https://www.youtube.com/watch?v=oJuGlqO85YI", "https://www.youtube.com/watch?v=z2_Lrg6rRks", "https://www.youtube.com/watch?v=uWoYIOcOpwU",
        "https://www.youtube.com/watch?v=eif_8yA2WhA", "https://www.youtube.com/watch?v=f1e8Ok4BmeU", "https://www.youtube.com/watch?v=u-GmuvAVKsE", "https://www.youtube.com/watch?v=pI8TZuxIZCc", "https://www.youtube.com/watch?v=68fgmFx5acg",
        "https://www.youtube.com/watch?v=0nPI4_GLkAM", "https://www.youtube.com/watch?v=6_Ab6ybbzFw", "https://www.youtube.com/watch?v=J8Hik8pGlQI", "https://www.youtube.com/watch?v=d1kWg-kNx3k", "https://www.youtube.com/watch?v=KgbY_hvI11o",
        "https://www.youtube.com/watch?v=HOGQPMmKB7Y", "https://www.youtube.com/watch?v=1QH7Aw5pA30", "https://www.youtube.com/watch?v=O8Zei-9o9cg", "https://www.youtube.com/watch?v=CAMWdvo71ls", "https://www.youtube.com/watch?v=t5D7XTHWAdw",
        "https://www.youtube.com/watch?v=_om0W6xzQd8", "https://www.youtube.com/watch?v=bFEP26jCtsQ", "https://www.youtube.com/watch?v=HGSAcjPj2YQ", "https://www.youtube.com/watch?v=U8BlNEKq0r8", "https://www.youtube.com/watch?v=KhJrWWbj6aw",
        "https://www.youtube.com/watch?v=mJ1N7-HyH1A", "https://www.youtube.com/watch?v=v-WcMQbXbKY", "https://www.youtube.com/watch?v=dgapVye0Ktw", "https://www.youtube.com/watch?v=moR4uw-NWLY", "https://www.youtube.com/watch?v=35nV_M3asRs",
        "https://www.youtube.com/watch?v=3P7aRlbBnrg", "https://www.youtube.com/watch?v=5BMnuvtdw1s", "https://www.youtube.com/watch?v=Sw1Flgub9s8", "https://www.youtube.com/watch?v=kD6TZpDaWr8", "https://www.youtube.com/watch?v=IbbhN4zFDfE",
        "https://www.youtube.com/watch?v=y4ZnV72Zco8", "https://www.youtube.com/watch?v=iJAxeafvn8Y", "https://www.youtube.com/watch?v=ohI8LKYlIyc", "https://www.youtube.com/watch?v=ATPulcGQ2SE", "https://www.youtube.com/watch?v=q07EmkvztQM",
        "https://www.youtube.com/watch?v=6THHrPyZQuQ", "https://www.youtube.com/watch?v=um8-0zDtdpQ", "https://www.youtube.com/watch?v=lUsBM7cS4lY", "https://www.youtube.com/watch?v=0JMdXFHo5SY", "https://www.youtube.com/watch?v=poKI_MY0Bkw",
        "https://www.youtube.com/watch?v=wMBNpVQ0k_k", "https://www.youtube.com/watch?v=KTsAmq9h7iM", "https://www.youtube.com/watch?v=R_RAWjqdgTs", "https://www.youtube.com/watch?v=Q1Euvef0UX0", "https://www.youtube.com/watch?v=1mAPHxL8KgM",
        "https://www.youtube.com/watch?v=xA1TJrx5ZI8", "https://www.youtube.com/watch?v=Jlq694r6OmA", "https://www.youtube.com/watch?v=KaLFZj3wPsc", "https://www.youtube.com/watch?v=aXsLlOPwe48", "https://www.youtube.com/watch?v=YUH9jD__qHY",
        "https://www.youtube.com/watch?v=vGGbp88ziXU", "https://www.youtube.com/watch?v=g3ENX3aHlqU", "https://www.youtube.com/watch?v=hjghAcOdGjQ", "https://www.youtube.com/watch?v=6CfRJSKk2Ls", "https://www.youtube.com/watch?v=-JWkQbRNtjs"
    ]
    download_clips(youtube_links)
